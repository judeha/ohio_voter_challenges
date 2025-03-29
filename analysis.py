import pandas as pd
import matplotlib.pyplot as plt

d1 = pd.read_csv('data/county_challenges_news.csv')
d1.columns = ['county', 'year', 'month', 'day','num', 'success']
d2 = pd.read_csv('data/county_challenges_official.csv')
d2.columns = ['county', 'year', 'month', 'day','num', 'success']

# get unique counties
unique_counties = list(d1.county.unique())
unique_counties += list(d2.county.unique())

# get counts for each county
compare_df = pd.DataFrame(columns=['county', 'news', 'official'])
for county in unique_counties:
    news = d1[d1.county == county].shape[0]
    official = d2[d2.county == county].shape[0]
    tmp_df = pd.DataFrame({'county': [county], 'news': [news], 'official': [official]})
    compare_df = pd.concat([compare_df, tmp_df],axis=0)

# plot
compare_df.plot(x='county', y=['news', 'official'], kind='bar')
plt.title('Figure 1: News vs Official Challenges')
plt.savefig('news_vs_official_counts.png')