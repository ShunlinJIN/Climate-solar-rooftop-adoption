#!/usr/bin/env python3
"""Render Figure 5 from the accompanying aggregate source data."""
from pathlib import Path
import argparse, json, hashlib, os, gc

# Also used directly by the public replication package. Set limits BEFORE
# pandas/NumPy import and OpenBLAS initialization, including inherited values.
for _thread_key in ('OPENBLAS_NUM_THREADS', 'OPENBLAS_DEFAULT_NUM_THREADS',
                    'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_thread_key] = '1'

import pandas as pd
import numpy as np
from figure5_helpers import *

def display_currency(e, g, rmb_per_usd):
    """Preserve native estimates and attach the units actually used for plotting."""
    e, g = e.copy(), g.copy()
    money = e.outcome.eq('electricity_expenditure_rmb_day')
    e['display_divisor'] = np.where(money, rmb_per_usd, 1.)
    e['display_unit'] = np.where(money, 'US$/day', 'kWh/day')
    for native, shown in [('estimate', 'display_estimate'),
                          ('std_error', 'display_std_error'),
                          ('conf_low', 'display_ci_low'),
                          ('conf_high', 'display_ci_high')]:
        e[shown] = e[native] / e.display_divisor
    money = g.outcome.eq('bill_rmb')
    g['display_divisor'] = g.display_divisor.astype(float)
    g.loc[money, 'display_divisor'] = rmb_per_usd
    for native, shown in [('estimate', 'display_estimate'),
                          ('std_error', 'display_std_error'),
                          ('ci_low', 'display_ci_low'),
                          ('ci_high', 'display_ci_high')]:
        g[shown] = g[native] / g.display_divisor
    g['display_unit'] = np.select(
        [money, g.outcome.eq('bill_income_pp')],
        ['US$/month', 'percentage points'], default='10 kWh/month')
    return e, g

def extended_panel_e(fig, ax, source):
    # One shared numerical axis: kWh/day and converted US$/day, as in Notes.
    # Match panels d and f: colored points and gray confidence intervals.
    # Larger points and thicker error bars match the enlarged typography.
    # Cap dimensions change only visually; confidence-limit endpoints do not.
    box=ax.get_position(); ax.set_axis_off()
    panel=fig.add_axes([box.x0, box.y0, box.width, box.height*.73])
    ax.text(-.17,1.045,'e',transform=ax.transAxes,ha='left',va='bottom',fontsize=FONT_PANEL,fontweight='bold')
    ax.set_title('Electricity services and\ncosts by heat state',fontsize=FONT_TITLE,pad=8)
    panel.axvline(0,color=GRAY,ls='--',lw=.75,zorder=1)
    panel.set_ylim(-.43,1.43)
    panel.set_yticks([1,0])
    panel.set_yticklabels(['Non-extreme\ndays','Extreme-heat\ndays'],fontsize=FONT_TICK)
    panel.tick_params(axis='y',length=0,pad=6)
    style_axis(panel)
    groups=[('total_electricity_consumption_kwh','Total use',CORAL,.255),
            ('grid_import_kwh','Grid purchases',NAVY,.085),
            ('pv_self_consumption_kwh','Self-consumption',TEAL,-.085),
            ('electricity_expenditure_rmb_day','Expenditure',ORANGE,-.255)]
    handles=[]
    for outcome,label,color,offset in groups:
        z=source.loc[source.outcome.eq(outcome)].copy()
        if len(z)!=2 or z.heat_state.nunique()!=2:
            raise ValueError(f'Expected one estimate per heat state for {outcome}.')
        y=z.heat_state.map({'Non-extreme days':1.,'Extreme-heat days':0.}).to_numpy()+offset
        h=panel.errorbar(z.display_estimate,y,
                       xerr=np.array([z.display_estimate-z.display_ci_low,
                                      z.display_ci_high-z.display_estimate]),
                       fmt='o',color=color,markerfacecolor=color,
                       markeredgecolor=color,markeredgewidth=.6,
                       ecolor=GRAY,markersize=4.6,capsize=3.5,
                       elinewidth=1.35,label=label,zorder=4)
        for cap in h[1]:
            cap.set_markeredgewidth(1.2)
        handles.append(h)
    panel.set_xlim(-4.1,4.1); panel.set_xticks([-4,-2,0,2,4])
    panel.set_xlabel('Effect',fontsize=FONT_LABEL)
    panel.tick_params(axis='x',labelsize=FONT_TICK)
    ax.legend(handles=handles,loc='upper center',bbox_to_anchor=(.50,1.00),
              frameon=False,ncol=2,fontsize=FONT_SMALL,handlelength=.85,
              handletextpad=.6,columnspacing=.9,labelspacing=.25,borderaxespad=0)
    return panel

CAPTION='Fig. 5 | Alleviation of rural household energy poverty.\nNotes: This figure shows how rooftop solar and battery storage alleviate household energy poverty. Panel a shows monthly changes in recorded electricity expenditure around PV grid connection; panel b shows changes in the electricity-bill-to-income ratio; and panel c shows changes in total household electricity use and public-grid purchases. Panels a–c report event-study estimates. They compare each adopter’s outcomes with a no-connection counterfactual constructed from households that never connect and future adopters observed before connection. Event time is defined by the household’s PV grid-connection month. Month −1 is the reference period. Shaded bands indicate 95% confidence intervals. Panel d reports changes in non-PV income, PV export revenue, total income including PV revenue, and income including PV revenue net of electricity bill. Panel e reports the post-grid-connection effects on daily total electricity use, public-grid purchases, PV self-consumption and electricity expenditure separately for extreme-heat and non-extreme days. Points show coefficient estimates on a single axis. Total electricity use, public-grid purchases and PV self-consumption are expressed in kWh per day, and electricity expenditure in US$ per day. PV self-consumption is total electricity use minus public-grid purchases. Extreme-heat days are defined as days with daily mean temperature above 30°C; non-extreme days are all remaining days under this definition. Panel f reports imputation estimates for monthly indicators of electricity expenditure at or above 5% and 10% of fixed pre-adoption income, averaged over months +1 to +12 after grid connection and expressed in percentage points. Panel g reports 2SLS estimates linking extreme heat, RRPV adoption and household energy poverty, with bars showing coefficient estimates. Electricity expenditure is displayed in US$ per month, the electricity-bill-to-income ratio in percentage points, and total electricity use and public-grid purchases in units of 10 kWh per month; bar labels give coefficients in US$, percentage points and kWh. Panel h reports battery-supply outcomes among the respondents who experienced a recent outage. Panel i reports battery backup duration. Monetary values are converted at RMB 6.8 per US$1. Error bars in panels d–g indicate 95% confidence intervals for estimated effects.\n'

def main():
    root=Path(__file__).resolve().parents[1]
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--results',type=Path,default=root/'results')
    p.add_argument('--output',type=Path,default=root/'results')
    p.add_argument('--data-dir',type=Path,default=root/'data')
    p.add_argument('--existing-data',type=Path)
    p.add_argument('--rmb-per-usd',type=float,default=6.8)
    p.add_argument('--png-dpi',type=png_dpi_value,default=300,
                   help='PNG preview DPI (default: 300); automatic reduction on MemoryError. PDF/SVG remain vector.')
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    if not np.isfinite(args.rmb_per_usd) or args.rmb_per_usd<=0: raise ValueError('Invalid currency conversion.')
    existing_path=args.existing_data or args.data_dir/'figure5_plot_data.csv'
    existing=pd.read_csv(existing_path,low_memory=False)
    data=load_final_data(existing_path)
    e=pd.read_csv(args.results/'Figure5_panel_e_source_data_v3.csv')
    g=pd.read_csv(args.data_dir/'figure5_panel_g.csv')
    e,g=display_currency(e,g,args.rmb_per_usd)
    burden=pd.read_csv(args.results/'Figure5_panel_f_source_data.csv')
    if len(e)!=8 or set(e.heat_state)!={'Non-extreme days','Extreme-heat days'}:raise ValueError('Panel e requires eight verified state-specific estimates.')
    set_style()
    fig,axes=plt.subplots(3,3,figsize=(12.3,11.2))
    a,b,c,d,ee,f,gg,h,i=axes.ravel()
    fig.subplots_adjust(left=.175,right=.98,top=.94,bottom=.075,wspace=.75,hspace=.70)
    event_panel(a,data['monthly_dynamic'],'electricity_bill_rmb','a','Electricity expenditure','Effect (US$/month)',scale=args.rmb_per_usd)
    event_panel(b,data['monthly_dynamic'],'bill_income_ratio_current_pct','b','Electricity-bill-to-income\nratio','Effect (percentage points)')
    panel_c(c,data['monthly_dynamic']);panel_d(d,data['income_static'],args.rmb_per_usd)
    extended_panel_e(fig,ee,e);panel_f(f,burden);iv_panel(gg,g)
    bar_distribution(h,outage_summary(data['supply']),'h','Battery supply\nduring outages','Respondents (%)',[TEAL,ORANGE,NAVY])
    bar_distribution(i,duration_distribution(data['duration']),'i','Reported backup\nduration','Respondents (%)',[LIGHT_GRAY,BLUE,DEEP_BLUE,NAVY])
    full_export=save_formats(fig,args.output,'Figure_5',png_dpi=args.png_dpi)
    plt.close(fig)
    del fig,axes,a,b,c,d,ee,f,gg,h,i
    gc.collect()
    caption=CAPTION.replace('RMB 6.8 per US$1',f'RMB {args.rmb_per_usd:g} per US$1')
    (args.output/'Figure_5_caption.txt').write_text(caption,encoding='utf-8')
    print(args.output.resolve())

if __name__=='__main__':main()
