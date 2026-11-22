import sys, os
sys.path.insert(0, os.path.abspath('.'))
import streamlit as st
from streamlit.testing.v1 import AppTest
import scoring as sc

app_file = os.path.abspath('app.py')

print('=== 1. Testing Full App Flow in Kannada ===')
at_kn = AppTest.from_file(app_file)
at_kn.run()
assert len(at_kn.exception) == 0, f'Home page error: {at_kn.exception}'

# Click Start Recommendation (ಶಿಫಾರಸು ಪ್ರಾರಂಭಿಸಿ)
at_kn.button[0].click().run()
assert len(at_kn.exception) == 0, f'Form page error: {at_kn.exception}'

# Submit form
go_btn = [b for b in at_kn.button if 'go_btn' in (b.key or '')][0]
go_btn.click().run()
assert len(at_kn.exception) == 0, f'Results page error: {at_kn.exception}'
assert at_kn.session_state.get('go') is True

# Verify "New recommendation" button works
new_rec_btn = [b for b in at_kn.button if 'new_rec' in (b.key or '')][0]
new_rec_btn.click().run()
assert len(at_kn.exception) == 0, f'New rec button error: {at_kn.exception}'
assert 'go' not in at_kn.session_state
print('✓ Kannada full flow (Home -> Form -> Results -> New Rec) PASS')

print('=== 2. Testing Full App Flow in English ===')
at_en = AppTest.from_file(app_file)
at_en.run()
lang_radio = [r for r in at_en.radio if r.key == 'lang_choice'][0]
lang_radio.set_value('English').run()
assert len(at_en.exception) == 0

# Click Start Recommendation
at_en.button[0].click().run()
assert len(at_en.exception) == 0

# Toggle Irrigation to True (I have irrigation)
irr_radio = [r for r in at_en.radio if 'irrigation' in (r.key or '')][0]
irr_radio.set_value(True).run()
assert len(at_en.exception) == 0
assert at_en.session_state['irrigation'] is True

# Submit
go_btn = [b for b in at_en.button if 'go_btn' in (b.key or '')][0]
go_btn.click().run()
assert len(at_en.exception) == 0
assert at_en.session_state['inputs']['irrigation'] is True

# Test Back to Home button from Form
new_rec_btn = [b for b in at_en.button if 'new_rec' in (b.key or '')][0]
new_rec_btn.click().run()
assert len(at_en.exception) == 0

home_btn = [b for b in at_en.button if 'back_home' in (b.key or '')][0]
home_btn.click().run()
assert len(at_en.exception) == 0
assert at_en.session_state['page'] == 'home'
print('✓ English full flow (Language switch -> Form -> Irrigation True -> Results -> New Rec -> Back Home) PASS')

print('=== 3. Testing All 10 Taluks & NASA Climate Insight ===')
taluks = list(sc.TALUK_TO_ZONE.keys())
for taluk in taluks:
    zone = sc.zone_for(taluk)
    for lang in ['en', 'kn']:
        zone_label = sc.WORDS[lang]['zones'].get(zone, zone)
        pct = sc.ZONE_FACTS[zone]
        assert isinstance(pct, (int, float))
assert len(taluks) == 10
print(f'✓ All {len(taluks)} taluks validated across both languages PASS')

print('=== ALL APP FLOW & STATE TESTS PASSED ===')
