import pandas as pd
import re


public = pd.read_csv('results/high school more info.csv')
private = pd.read_csv('results/private schools.csv')
fails = pd.read_csv('results/fails 2.csv', index_col=0)
high_schools = pd.read_csv('results/high schools.csv')
for i in range(len(high_schools)):
	n = 5 - len(str(high_schools.iloc[i, 2]))
	if n > 0:
		high_schools.iloc[i, 2] = '0'*n + str(high_schools.iloc[i, 2])

high_schools['ID'] = 'N/A'
for i in range(len(high_schools)):
	high_schools['ID'][i] = str([m.group() for m in re.finditer(r"ID=\w+\d+", high_schools['link'][i])][0].replace('ID=', ''))
public['ID'] = high_schools['ID']


public = public.drop_duplicates()
private = private.drop_duplicates()
high_schools = high_schools.iloc[public.index, :]


for i in fails.iloc[:, 0]:
	try:
		public = public.drop(i)
	except:
		pass
public.to_csv('results/public schools.csv', index=False)


public.reset_index().drop('index', axis=1)
private.reset_index().drop('index', axis=1)
high_schools.reset_index().drop('index', axis=1)


temp_pub = public[['school name', 'ID', 'Total Students']]
temp_pri = private[['school name', 'ID', 'Total Students']]
for i in range(len(private)):
	private['ID'][i] = str(private['ID'][i])
temp_pub['Nature'] = 'public'
temp_pri['Nature'] = 'private'


combine = pd.concat([temp_pub, temp_pri])
combine = combine.reset_index().drop('index', axis=1)
combine['Total Students'] = combine['Total Students'].replace(0, None)
combine['Total Students'] = combine['Total Students'].replace('–', None)
combine['Total Students'] = combine['Total Students'].replace('†', None)


out = pd.merge(combine, high_schools[['ID', 'city', 'state', 'zip code', 'address', 'contact', 'grades']], on=['ID'])
order = ['ID', 'school name', 'address', 'city', 'state', 'zip code', 'contact', 'grades', 'Nature', 'Total Students']
out = out[order]
out.columns = ['ID', 'school name', 'address', 'city', 'state', 'zip code', 'contact', 'grades', 'nature', 'size']


out.to_csv('results/useful info.csv', index=False)
