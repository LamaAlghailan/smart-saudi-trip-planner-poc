r"""Run with .venv\Scripts\python.exe -m streamlit run app.py."""
from collections import Counter
import json

import pandas as pd
import streamlit as st

from trip_planner.data import CSV_PATH, WVS_PATH, load_tourism, load_wvs
from trip_planner.engine import TripRequest, export_csv
from trip_planner.experiment import run_comparison, run_mode, save_experiment
from trip_planner.profiles import BASIC, WVS
from trip_planner.settings import load_settings

st.set_page_config(page_title='Rfqah | Grounded LLM Experiment', page_icon='🌿', layout='wide')


@st.cache_data
def sources(csv_stamp, wvs_stamp):
    items, audit = load_tourism()
    return items, audit, load_wvs()


def clear_result():
    st.session_state.pop('experiment', None)


def show_affinities(profile):
    for domain in ('hobbies', 'categories', 'environments'):
        rows = sorted(profile[domain].items(), key=lambda row: (-row[1], row[0]))
        st.markdown(f'**{domain.title()} prior**')
        if rows:
            st.dataframe(pd.DataFrame(rows, columns=['Dimension', 'Relative-derived affinity']),
                         hide_index=True, width='stretch')
        else:
            st.write('No eligible evidence; neutral 0.5 is used.')
    with st.expander('Source WVS evidence and eligibility'):
        st.dataframe(pd.DataFrame(profile['evidence']), hide_index=True, width='stretch')


def show_run(run, key):
    retrieval = run['retrieval']
    package = retrieval['candidate_package']
    st.subheader(run['mode'])
    st.markdown('**1. Factual Tourist Profile**')
    st.json(package['tourist_facts'])
    st.write(f"Trip: {package['trip_start']} through {package['trip_end']} · {package['trip_days']} days")
    stats = retrieval['stats']
    st.markdown('**Data-quality and date-filter diagnostics**')
    st.write(f"{len(audit)} source records → {stats['validated_active_count']} valid/active → {stats['before_date_filter']} distinct before date filtering → {stats['after_date_filter']} available during selected dates → {stats['city_count']} candidate cities → {stats['activity_count']} candidate activities")
    st.json({'source_records': len(audit), 'quarantined': sum(not r['eligible'] for r in audit), **stats})
    st.json({k: sum(r[k] for r in audit) for k in ('unknown_available_from', 'unknown_available_until', 'reversed_date_range', 'boolean_like_date')})
    if retrieval['wvs_profile'] is not None:
        st.markdown('**2. WVS Profile**')
        show_affinities(retrieval['wvs_profile'])
        st.caption('A weak group-level prior based on country of birth, not nationality or literal individual preferences.')
    for warning in retrieval['warnings']:
        st.warning(warning)
    st.markdown('**3. Filtered Candidate Cities**')
    cities = package['candidate_cities']
    if cities:
        st.dataframe(pd.DataFrame([{'Candidate city': c['city'], 'Retrieval score': c['retrieval_score'],
                                   'Supplied activities': len(c['candidate_activities'])} for c in cities]),
                     hide_index=True, width='stretch')
    else:
        st.info('No viable candidate cities. No final destination was chosen.')
    st.markdown('**4. Candidate Activities per City**')
    for city in cities:
        st.markdown(f"**{city['city']}**")
        st.dataframe(pd.DataFrame([{k: a[k] for k in ('ItemId', 'ItemName', 'Category', 'Environment',
                                 'GroupCost', 'DurationMinutes', 'available_from', 'available_until', 'opens', 'closes', 'retrieval_score')}
                                  for a in city['candidate_activities']]), hide_index=True, width='stretch')
    st.markdown('**5. Candidate retrieval scores**')
    if retrieval['wvs_profile'] is not None:
        with st.expander('WVS mapping debug: candidate activity rules and matched priors'):
            st.json({a['ItemId']: {'ItemName': a['ItemName'], **a['mapping_debug']}
                     for c in cities for a in c['candidate_activities']})
    st.json(package['retrieval_weights'])
    st.json(package['scoring'])
    st.caption('Scores order retrieval relevance. The LLM can select any supplied city; rank 1 is not a final recommendation.')
    with st.expander('City score components'):
        st.json({c['city']: c['city_profile'] for c in cities})
    with st.expander('Full retrieval package (internal diagnostics)'):
        st.json(package)
        st.download_button('Download candidate package', json.dumps(package, ensure_ascii=False, indent=2),
                           f'{key}_candidates.json', 'application/json', key=f'{key}_candidates')
    with st.expander('Compact LLM payload and request-size diagnostics'):
        st.json(run['request_size'])
        st.json(run['llm_candidate_package'])
    st.caption(f"Full retrieval: {retrieval['stats']['city_count']} cities, {retrieval['stats']['activity_count']} activities, "
               f"{retrieval['stats']['package_bytes']:,} JSON bytes. Provider: {run['provider']}; model: {run['model'] or 'not configured'}.")
    st.markdown('**6. LLM-selected destination**')
    answer = run['llm']
    if answer is None:
        st.info(run['message'])
        if run.get('error_diagnostics'):
            st.markdown('**Sanitized provider error diagnostics**')
            st.json(run['error_diagnostics'])
        st.markdown('**7. LLM reasoning**')
        st.write('No LLM response.')
        st.markdown('**8. Final itinerary**')
        st.write('Not generated. Candidate retrieval does not choose a destination or create a substitute itinerary.')
        st.markdown('**9. Validation results**')
        st.write('Post-LLM validation not run because no LLM output is available.')
        return
    if answer.get('is_mock'):
        st.warning('TEST MOCK — not real LLM output.')
    output = answer['output']
    validation = run['validation']
    if not validation['valid']:
        st.error('LLM output failed validation and is not accepted as a final itinerary.')
        st.write(run['message'])
    st.write(output.get('selected_destination', 'Invalid response') if isinstance(output, dict) else 'Invalid response')
    st.markdown('**7. LLM reasoning**')
    if isinstance(output, dict):
        reasons = output.get('destination_reasoning')
        if isinstance(reasons, list):
            for reason in reasons:
                st.write(reason)
        else:
            st.write('No valid decision summary returned.')
        st.caption(f"Alternative: {output.get('alternative_destination') or 'None'}")
    st.markdown('**8. Final itinerary**')
    if validation['valid']:
        st.metric('Total group activity cost', f"SAR {validation['total_group_cost']:,.2f}")
        for stop in validation['validated_itinerary']:
            with st.container(border=True):
                st.markdown(f"**{stop['date']} · Day {stop['day']} · {stop['start']}–{stop['end']} · {stop['ItemName']}**")
                st.write(stop['llm_reason'])
                st.caption(f"{stop['category']} · {stop['environment']} · SAR {stop['group_cost']:g} for the group · {stop['ItemId']}")
        st.download_button('Download validated itinerary CSV', export_csv(validation['validated_itinerary']),
                           f'{key}_itinerary.csv', 'text/csv', key=f'{key}_itinerary')
    else:
        st.write('No validated itinerary is available. Review the violations below.')
    st.markdown('**9. Validation results**')
    if validation['valid']:
        st.success('Grounding and supplied factual constraints passed.')
    else:
        st.dataframe(pd.DataFrame(validation['constraint_violations']), hide_index=True, width='stretch')
    for warning in validation['warnings']:
        st.warning(warning)
    st.json({k: validation[k] for k in ('valid', 'invalid_item_ids', 'unknown_item_ids',
                                      'unsupplied_item_ids', 'duplicate_item_ids', 'total_group_cost')})
    st.caption(f"LLM latency: {run['llm_latency_seconds']:.2f}s. Total: {run['total_latency_seconds']:.2f}s.")
    with st.expander('Raw LLM output and metadata'):
        st.json(answer)


st.caption('RIFQAH / GROUNDED LLM EXPERIMENT')
st.title('What changes when the LLM receives a WVS prior?')
st.write('The same factual trip inputs feed candidate retrieval, then an LLM chooses the destination and itinerary.')
try:
    items, audit, wvs = sources(CSV_PATH.stat().st_mtime_ns, WVS_PATH.stat().st_mtime_ns)
    settings = load_settings()
except (OSError, ValueError, KeyError) as exc:
    st.error(f'Could not load local data or configuration: {exc}')
    st.stop()
country_values = sorted({r['Birth Country'] for r in wvs['HOBBY_RESULTS']})
planner_tab, quality_tab, evidence_tab = st.tabs(['Experiment', 'Data quality', 'WVS evidence'])

with planner_tab:
    mode = st.radio('Mode', [BASIC, WVS], key='mode', horizontal=True, on_change=clear_result)
    st.caption(f'Provider: {settings.provider_name} | Model: {settings.model or "not configured"}')
    if settings.llm_available:
        st.info(f'{settings.provider_name} configured: {settings.model}. Running an experiment sends the factual inputs and displayed candidate package to {settings.provider_name}. Comparison runs two requests.')
    else:
        st.warning(settings.unavailable_reason + ' No mock itinerary will be shown.')
    with st.form('trip_form'):
        left, middle, right = st.columns(3)
        with left:
            country = st.selectbox('Birth Country', ['Select birth country', 'Not listed'] + country_values, key='birth_country')
            start_date = st.date_input('Start Date (required)', value=None, key='start_date')
            end_date = st.date_input('End Date (required)', value=None, key='end_date')
            budget = st.number_input('Total activity budget (SAR for the whole group)', 0.0, 100000.0, 500.0, step=50.0, key='budget')
        with middle:
            adults = st.number_input('Number of adults (18+)', 1, 50, 1, key='adults')
            children = st.number_input('Number of children (under 18)', 0, 49, 0, key='children')
            youngest = st.number_input('Youngest traveler age (optional)', min_value=0, max_value=120,
                                       value=None, placeholder='Not supplied', key='youngest')
        with right:
            oldest = st.number_input('Oldest traveler age (optional)', min_value=18, max_value=120,
                                     value=None, placeholder='Not supplied', key='oldest')
        run_single = st.form_submit_button('Run experiment', type='primary')
        run_both = st.form_submit_button('Compare both modes')
    st.caption('Budget assumes source Price is SAR per traveler. Group cost includes adults and children at the same source price. No booking, real-time price, or driving-route verification is performed.')
    if run_single or run_both:
        clear_result()
        try:
            request = TripRequest(birth_country='' if country == 'Select birth country' else country,
                                  end_date=end_date, budget=budget, adults=int(adults), children=int(children),
                                  youngest_age=int(youngest) if youngest is not None else None,
                                  oldest_age=int(oldest) if oldest is not None else None, start_date=start_date)
            with st.spinner('Retrieving grounded candidates and running the configured experiment...'):
                record = run_comparison(items, request, wvs, settings) if run_both else {
                    'kind': 'single', 'runs': [run_mode(items, request, wvs, mode, settings)]}
            st.session_state['experiment'] = record
            try:
                path = save_experiment(record)
                record['saved_path'] = str(path)
            except OSError:
                record['save_error'] = 'The run is available in this session, but could not be saved to outputs/experiments.'
        except ValueError as exc:
            st.error(str(exc))
    if 'experiment' in st.session_state:
        record = st.session_state['experiment']
        st.caption('Results reflect the last submitted factual profile. Submit again after changes.')
        if record.get('save_error'):
            st.warning(record['save_error'])
        elif record.get('saved_path'):
            st.caption(f"Saved experiment: {record['saved_path']}")
        if record['kind'] == 'comparison':
            comparison = record['comparison']
            st.subheader('Side-by-side comparison')
            st.write(comparison['llm_comparison_status'])
            st.caption(comparison['interpretation'])
            st.dataframe(pd.DataFrame([comparison['basic'], comparison['wvs']]).drop(columns=['characteristics']),
                         hide_index=True, width='stretch')
            st.json({k: comparison[k] for k in ('candidate_city_overlap', 'candidate_set_overlap',
                                                'itinerary_overlap', 'destination_changed', 'both_itineraries_valid')})
            with st.expander('Itinerary characteristics (validated outputs only)'):
                st.json({k: comparison[k]['characteristics'] for k in ('basic', 'wvs')})
            columns = st.columns(2)
            for index, (column, run) in enumerate(zip(columns, record['runs'])):
                with column:
                    show_run(run, f'comparison_{index}')
        else:
            show_run(record['runs'][0], 'single')
        st.download_button('Download experiment record', json.dumps(record, default=str, ensure_ascii=False, indent=2),
                           'rifqah_experiment.json', 'application/json', key='record_download')
    else:
        st.info('Enter factual trip information to inspect candidate retrieval or run the two-mode comparison.')

with quality_tab:
    st.subheader('Source quality and planning eligibility')
    invalid = [r for r in audit if not r['eligible']]
    a, b, c = st.columns(3)
    a.metric('Source records', len(audit))
    b.metric('Pass validation', len(items))
    c.metric('Quarantined', len(invalid))
    st.write(f"{sum(i['IsActive'] for i in items)} validated records are marked active. Dates and group constraints reduce the usable set further.")
    st.caption('Raw files are read only. Invalid records are excluded, with no guessed column shifts. Coordinate bounds do not verify exact locations.')
    counts = Counter(issue for r in invalid for issue in r['issues'].split('; '))
    st.dataframe(pd.DataFrame(counts.most_common(), columns=['Issue', 'Records']), hide_index=True, width='stretch')
    st.dataframe(pd.DataFrame(audit), hide_index=True, width='stretch')
    st.download_button('Download quality audit', pd.DataFrame(audit).to_csv(index=False).encode('utf-8-sig'),
                       'tourism_quality_audit.csv', 'text/csv')

with evidence_tab:
    st.subheader('Explore the WVS evidence')
    st.write('Country of birth (Q266) is not confirmed nationality. Group signals do not establish an individual preference or causation.')
    evidence_country = st.selectbox('Country to inspect', country_values, key='evidence_country')
    for sheet, title in [('HOBBY_RESULTS', 'Hobbies'), ('CATEGORY_RESULTS', 'Categories'), ('ENVIRONMENT_RESULTS', 'Environments')]:
        st.markdown(f'**{title}**')
        st.dataframe(pd.DataFrame([r for r in wvs[sheet] if r['Birth Country'] == evidence_country]),
                     hide_index=True, width='stretch')
    st.markdown('**Statistical effects by hobby**')
    st.dataframe(pd.DataFrame(wvs['STATISTICAL_EFFECTS']), hide_index=True, width='stretch')
    st.caption('Raw N, Effective N, coverage, eligibility, and ranks are preserved. Missing/ineligible evidence is neutral, not inferred as a preference. Phase 1 mapping data and survey validation are not supplied.')
