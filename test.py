import json
with open('00733.json','r') as f:
    data = json.load(f)
with open('00733.csv','w') as f:
    output = []
    for stock,value in data.items():
        for date,broker in value.items():
            s=stock+","+date+","+",".join(broker)+"\n"
            output.append(s)
    f.writelines(output)