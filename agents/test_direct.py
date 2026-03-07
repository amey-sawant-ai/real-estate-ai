import sys
sys.path.append('.')
from main import analyze_sequence, LocationQuery

if __name__ == '__main__':
    payload = LocationQuery(query="New York", budget="1M USD", risk="high")
    try:
        report = analyze_sequence(payload)
        print("\nSuccess!")
        print("Keys in report:", report['report'].keys())
        if 'scenario_analysis' in report['report']:
            print("Scenario Analysis exists!")
        else:
            print("Scenario Analysis MISSING!")
    except Exception as e:
        import traceback
        traceback.print_exc()
