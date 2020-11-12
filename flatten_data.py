#%% 
import os
import json
from datetime import date

with open("data/dict.json") as f:
    data = json.load(f)
with open("docs/dict.json", "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=True)

with open("docs/last-updated.json", "w") as f:
    json.dump([str(date.today())], f)


def get_url(page):
    for src, items in page.items():
        if src == 'url':
            return items[0]
    raise Exception('No url found')
#%%
out = {}
for page in data:
    url = get_url(page)
    for cat, items in page.items():
        if items is None or cat == 'url' or cat == 'date': continue
        
        for item in items:
            item = item.strip()
            if len(item) > 1:
                if item not in out:
                    out[item] = { 
                        'category': cat,
                        'src': url
                    }
                else:
                    out[item]['category'] += f', {cat}'


out = sorted( ((item, d['category'], d['src']) for item, d in out.items()), reverse=True)


#%%
# Save as json for web app
with open("docs/ptt-terms.json", "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=True)


# Save as tsv
with open("docs/ptt-terms.tsv", "w") as f:
    f.write('item\tcategory\tsrc\n')
    for item, category, src in out:
        f.write(f'{item}\t{category}\t{src}\n')
