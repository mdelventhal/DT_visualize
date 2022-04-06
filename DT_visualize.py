import numpy as np
import streamlit as st
import pandas as pd
import altair as alt

@st.cache
def load_data(filen):
    datain = pd.read_csv(filen)
    datain["modeled_Death_Rate"] = \
            datain["cdeathProjection"]
    for col in datain.columns:
        datain.loc[datain[col] == "NA",col] = np.NaN
    datain["CDRlabel"] = "Deaths"
    datain["CBRlabel"] = "Births"
    datain["CDRlabel2"] = "Modeled Deaths"
    datain["CBRlabel2"] = "Modeled Births"
    return datain

@st.cache
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')


def countryselecter(datadf,countrylist):
    selection = np.ones((len(datadf),)) == 0
    
    for country in countrylist:
        selection |= np.array(datadf.country) == country
    
    return selection

def plotter(datadf,selection,xlimits,ylimits,toggles):
    
    chart = alt.Chart(datadf.loc[selection])
    
    xscaler = alt.Scale(domain=[xlimits[0],xlimits[1]],clamp=True)
    
    yscaler = alt.Scale(domain=[ylimits[0],ylimits[1]],clamp=True)
    
    pointb = chart.mark_point(size=2).encode(
        x = alt.X('year',scale=xscaler,axis=alt.Axis(format="d")),
        y = alt.Y('Crude_Birth_Rate',scale=yscaler,axis=alt.Axis(title="yearly rate per 1,000 residents")),
        color='country',
        shape=alt.Shape('CBRlabel',scale=alt.Scale(domain=["Births","Deaths"],range=['circle','triangle-down']),legend=alt.Legend(title="Raw data")),
        tooltip=[alt.Tooltip('year', format='d'),
                 alt.Tooltip('Crude_Birth_Rate',format='.2f',title='Crude Birth Rate'),
                 alt.Tooltip('country')]).interactive()

    linebm = chart.mark_line(strokeWidth=1).encode(
        x = alt.X('year',scale=xscaler,axis=alt.Axis(format="d")),
        y = alt.Y('modeled_Birth_Rate',scale=yscaler,axis=alt.Axis(title="yearly rate per 1,000 residents")),
        color='country',
        strokeDash=alt.StrokeDash('CBRlabel2',
                                 scale=alt.Scale(domain=["Modeled Births","Modeled Deaths"],range=[[4,2],[1,3,1]]),
                                 legend=alt.Legend(title="Modeled")),
        tooltip=[alt.Tooltip('year', format='d'),
                 alt.Tooltip('Crude_Birth_Rate',format='.2f',title='modeled CBR'),
                 alt.Tooltip('country')]).interactive()

    pointd = chart.mark_point(size=2).encode(
        x = alt.X('year',scale=xscaler,axis=alt.Axis(format="d")),
        y = alt.Y('Crude_Death_Rate',scale=yscaler,axis=alt.Axis(title="yearly rate per 1,000 residents")),
        color='country',
        shape=alt.Shape('CDRlabel',scale=alt.Scale(domain=["Births","Deaths"],range=['circle','triangle-down']),legend=alt.Legend(title="Raw data")),
        tooltip=[alt.Tooltip('year', format='d'),
                 alt.Tooltip('Crude_Birth_Rate',format='.2f',title='Crude Death Rate'),
                 alt.Tooltip('country')]).interactive()

    linedm = chart.mark_line(strokeWidth=1).encode(
        x = alt.X('year',scale=xscaler,axis=alt.Axis(format="d")),
        y = alt.Y('modeled_Death_Rate',scale=yscaler,axis=alt.Axis(title="yearly rate per 1,000 residents")),
        color='country',
        strokeDash=alt.StrokeDash('CDRlabel2',
                                 scale=alt.Scale(domain=["Modeled Births","Modeled Deaths"],range=[[4,2],[1,3,1]]),
                                 legend=alt.Legend(title="Modeled")),
        tooltip=[alt.Tooltip('year', format='d'),
                 alt.Tooltip('Crude_Birth_Rate',format='.2f',title='modeled CDR'),
                 alt.Tooltip('country')]).interactive()
    
    varcount = 0
    if toggles[0]:
        if varcount == 0:
            chartout = pointd
        else:
            chartout += pointd
        varcount += 1
    
    if toggles[1]:
        if varcount == 0:
            chartout = pointb
        else:
            chartout += pointb
        varcount += 1
    
    if toggles[2]:
        if varcount == 0:
            chartout = linedm
        else:
            chartout += linedm
        varcount += 1
        
    if toggles[3]:
        if varcount == 0:
            chartout = linebm
        else:
            chartout += linebm
        varcount += 1
    
    if varcount == 0:
        chartout = None
    return chartout,datadf.loc[selection,["year","country"] + list(np.array(["Crude_Death_Rate","Crude_Birth_Rate",
                                                        "modeled_Death_Rate","modeled_Birth_Rate"])[toggles])]

    
    
data = load_data("Dem_Trans_data.csv")

data_country = pd.read_csv("DT_data_byCountry.csv")



with st.sidebar:
    st.write('Variables to include')
    col1, col2 = st.columns(2)
    with col1:
        CDR_show = st.checkbox('Crude Death Rate',value=True)

    with col2:
        CBR_show = st.checkbox('Crude Birth Rate',value=True)

    with col1:
        CDR_modeled_show = st.checkbox('Modeled CDR',value=True)

    with col2:
        CBR_modeled_show = st.checkbox('Modeled CBR',value=True)


        
contain1 = st.container()
contain2 = st.container()

with contain1:
    st.write('### Demographic transition chart')
    countrylist = st.multiselect('Countries to plot',data_country['country'],'United Kingdom')

select = countryselecter(data,countrylist)
bycountry_select = countryselecter(data_country,countrylist)

data_country_todisplay = pd.DataFrame(data_country.loc[bycountry_select])



try:
    data_ylims = [ 0,1.02*np.nanmax(np.array(data.loc[select,["Crude_Birth_Rate","Crude_Death_Rate","modeled_Birth_Rate","modeled_Death_Rate"]]
                                                    ))  ]
except:
    data_ylims = [0,60]



try:
    data_xlims = [ np.min(np.array(data.loc[select,["year"]]
                                                    )),
                            np.max(np.array(data.loc[select,["year"]]
                                                    ))
                                                        ]
except:
    data_xlims = [1600,2010]

with st.sidebar:
    ylower,yupper = st.slider('rate per 1,000 population (y-axis limits)',0,80,(int(data_ylims[0]),int(data_ylims[1])))


with contain2:
    xlower,xupper = st.slider('year (x-axis limits)',1500,2020,(int(data_xlims[0]),int(data_xlims[1])))


    



newchart,charteddata = plotter(data,select,[xlower,xupper],[ylower,yupper],[CDR_show,CBR_show,CDR_modeled_show,CBR_modeled_show])

with contain1:
    try: 
        st.altair_chart(newchart.properties(height=400),use_container_width=True)
    except: 
        ""


charted_csv = convert_df(charteddata)

full_yearly_csv = convert_df(data)


col_1_1,col_1_2 = st.columns(2)

with col_1_1:
    st.download_button(
         label="Download charted data",
         data=charted_csv,
         file_name='DT_charted_data.csv',
         mime='text/csv',
     )

with col_1_2:
    st.download_button(
         label="Download full yearly dataset",
         data=full_yearly_csv,
         file_name='Dem_Trans_Data.csv',
         mime='text/csv',
     )

styled = data_country_todisplay[["country",
                                 "CDR_start","CDR_end",
                                 "pre_CDR","post_CDR",
                                 "CBR_start","CBR_end",
                                 "pre_CBR","post_CBR"
                                 ]].style.hide_index()  \
                        .format("{:.2f}", subset=["pre_CDR","post_CDR","pre_CBR","post_CBR"])

styled.set_table_styles([
    {'selector': 'th.col_heading', 'props': 'text-align: center;'},
    {'selector': 'th.col_heading.level0', 'props': 'font-size: .8em;'},
    {'selector': 'td', 'props': 'text-align: center; font-size: .8em;'},
], overwrite=False)

st.write(" ")
st.write('### Summary by country')
st.write(styled.to_html(), unsafe_allow_html=True)


selected_csv = convert_df(data_country_todisplay[["country",
                                 "CDR_start","CDR_end",
                                 "pre_CDR","post_CDR",
                                 "CBR_start","CBR_end",
                                 "pre_CBR","post_CBR"
                                 ]])

full_summary_csv = convert_df(data_country[["country",
                                 "CDR_start","CDR_end",
                                 "pre_CDR","post_CDR",
                                 "CBR_start","CBR_end",
                                 "pre_CBR","post_CBR"
                                 ]])


st.write(" ")

col_2_1,col_2_2 = st.columns(2)

with col_2_1:
    st.download_button(
         label="Download selected summary data",
         data=charted_csv,
         file_name='DT_selected_summary.csv',
         mime='text/csv',
     )

with col_2_2:
    st.download_button(
         label="Download complete country summary table",
         data=full_summary_csv,
         file_name='DT_summary_bycountry.csv',
         mime='text/csv',
     )


