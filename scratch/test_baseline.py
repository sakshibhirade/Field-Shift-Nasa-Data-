import sys
sys.path.insert(0, '.')
import json
import scoring as sc

baseline_path = r'C:\Users\HP\.gemini\antigravity\brain\702f6f7b-9c45-46ff-8767-2242009a9ec4\scratch\baseline_full.json'
with open(baseline_path, 'r', encoding='utf-8') as f:
    baseline = json.load(f)

zones = ['Belagavi', 'Athani', 'Khanapur']
soils = ['black', 'red', 'sandy']
seasons = ['kharif', 'rabi']
crops = list(sc.crop_info.keys()) + list(sc.other_info.keys())
irrigations = [False, True]
priorities = ['balanced', 'soil_health', 'save_water', 'safe_harvest']

diffs = 0
tested = 0

for zone in zones:
    for soil in soils:
        for season in seasons:
            for last_crop in crops:
                for priority in priorities:
                    for irrigation in irrigations:
                        k = f'{zone}|{soil}|{season}|{last_crop}|{priority}|{irrigation}'
                        res = sc.recommend(zone, soil, season, last_crop, irrigation=irrigation, priority=priority, lang='en')
                        
                        curr_scores = []
                        for item in res['ranked']:
                            p_dict = {}
                            for part_name, part_val in item['parts'].items():
                                if part_name == 'rotation':
                                    p_dict[part_name] = [part_val.points, part_val.why, part_val.confidence]
                                else:
                                    p_dict[part_name] = [part_val.points, part_val.why]
                            curr_scores.append([item['crop'], item['total'], p_dict])
                        
                        b_val = baseline[k]
                        if b_val['scores'] != curr_scores or b_val['warnings'] != res['warnings']:
                            diffs += 1
                        tested += 1

print(f'Tested: {tested}, Diffs: {diffs}')
assert tested == 1584
assert diffs == 0
print('1,584 COMBINATION REGRESSION TEST PASSED 100% BYTE-FOR-BYTE!')
