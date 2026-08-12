dealers = [{"name":"杭州华联","region":"华东","sales":3200},
           {"name":"杭州佰诚","region":"华东","sales":3300},
           {"name":"北京光彩","region":"华北","sales":3400},
           {"name":"苏州优品","region":"华东","sales":3500},
           {"name":"福建水下","region":"华南","sales":3600},
           {"name":"阜阳情谊","region":"华中","sales":3700},
           {"name":"上海来财","region":"华东","sales":3800},
           {"name":"湖州满天","region":"华东","sales":3900},
           {"name":"宝鸡飞天","region":"华西","sales":4000},
           {"name":"河南有礼","region":"华中","sales":4100}
           ]

totalsales = 0
n = 0
while n < len(dealers):
    totalsales += dealers[n]['sales']
    n += 1
    
print('总销量：%d' %(totalsales))
print('平均销量：%.2f' %(totalsales/len(dealers)))

#销量top3
sort = sorted(dealers,key=lambda d:d['sales'],reverse=True)
print('销量top3')
for n1 in sort[:3]:
    print(f"{n1['name']} 销量:{n1['sales']}")

#每个区域的销量合计
region_sales = {}
for ns in dealers:
    region_sales[ns['region']] = region_sales.get(ns['region'],0) + ns['sales']

for r , s in region_sales.items():
    print(f"{r}:{s}")
