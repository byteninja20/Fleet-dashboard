"""Rebuild index.html from the fleet CSV.  Usage: python build.py [path/to/sheet.csv]"""
import sys, json, glob
import pandas as pd

src = sys.argv[1] if len(sys.argv) > 1 else (glob.glob('data/*.csv') or [None])[0]
if not src: sys.exit('Put your CSV in the data/ folder or pass its path.')
df = pd.read_csv(src); df.columns = [c.strip() for c in df.columns]
d = df.dropna(subset=['Date']).copy()
d['D'] = pd.to_datetime(d['Date'], format='mixed', dayfirst=True)

def num(x):
    if pd.isna(x): return 0.0
    try: return float(str(x).replace('₹', '').replace(',', '').strip())
    except ValueError: return 0.0
def s(x): return '' if pd.isna(x) else str(x).strip()

brand = d.groupby('Vehicle No.')['Vehicle Brand'].agg(lambda v: v.dropna().mode().iloc[0] if v.notna().any() else '').to_dict()
NON_FLEET = {'2043'}          # vehicles that are not part of the fleet (shown as notes only)
recs = []
for _, r in d.sort_values('D').iterrows():
    ds, vs, cv = s(r['Driver Status']), s(r['Vehicle Status']), s(r['Coverage Type'])
    mg = s(r['MG Received?']).lower()
    net, mga, trips = num(r['Net Earning']), num(r['MG Amount']), num(r['Number of Trips'])
    earn = net + (mga if mg == 'yes' else 0)                       # MG counts only once received
    te = num(r['Total Expenses'])
    exp = te if te > 0 else num(r['Toll']) + num(r['Other Expense'])
    if ds == 'Weekly Off': sc = 'Weekly Off'
    elif vs == 'Off-Road (Breakdown)': sc = 'Off-Road (Breakdown)'
    elif vs == 'Not Operated': sc = 'Not Operated'
    elif cv == 'Substitute Driver': sc = 'Covered by Substitute'
    elif vs == 'Running' or earn > 0 or trips > 0: sc = 'Normal Run'
    else: sc = 'Note'
    v = s(r['Vehicle No.'])
    recs.append(dict(date=r['D'].strftime('%Y-%m-%d'), dateLabel=r['D'].strftime('%d %b'), day=s(r['Day']),
        vehicle=v, hub=s(r['Vehicle Hub']), brand=brand.get(v, ''), actual=s(r['Actual Driver']), scenario=sc,
        earn=round(earn), exp=round(exp), trips=int(trips), mgRecv=round(mga if mg == 'no' else 0),
        platform=s(r['Platform']), remarks=s(r['Remarks']), fleet=v not in NON_FLEET))

vehicles = []
for r in recs:
    if r['fleet'] and r['vehicle'] not in vehicles: vehicles.append(r['vehicle'])
dates = sorted({r['date'] for r in recs})
payload = json.dumps(dict(records=recs, vehicles=vehicles, dates=dates,
                          hubs=sorted({r['hub'] for r in recs if r['hub']}))).replace('</script', '<\\/script')
a, b = pd.Timestamp(dates[0]), pd.Timestamp(dates[-1])
rng_short = f"{a:%d}–{b:%d %b}" if a.month == b.month else f"{a:%d %b} – {b:%d %b}"
html = open('template.html', encoding='utf-8').read()
html = (html.replace('__PAYLOAD__', payload).replace('__RANGE_SHORT__', rng_short)
            .replace('__RANGE__', f"{a:%d} – {b:%d %b %Y}" if a.month == b.month else f"{a:%d %b} – {b:%d %b %Y}"))
open('index.html', 'w', encoding='utf-8').write(html)
print(f"index.html built: {len(recs)} rows, {dates[0]} to {dates[-1]}")
