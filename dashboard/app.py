"""
交易数据面板 - Streamlit
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'trades.db')


def get_connection():
    return sqlite3.connect(DB_PATH)


@st.cache_data(ttl=60)
def load_trades():
    """加载交易数据"""
    conn = get_connection()
    df = pd.read_sql_query('''
        SELECT * FROM trades ORDER BY timestamp DESC
    ''', conn)
    conn.close()
    if not df.empty:
        df['datetime'] = pd.to_datetime(df['datetime'])
    return df


@st.cache_data(ttl=60)
def load_positions():
    """加载持仓数据"""
    conn = get_connection()
    df = pd.read_sql_query('''
        SELECT * FROM positions ORDER BY timestamp DESC
    ''', conn)
    conn.close()
    return df


@st.cache_data(ttl=60)
def load_balance():
    """加载余额数据"""
    conn = get_connection()
    df = pd.read_sql_query('''
        SELECT * FROM balance_snapshots ORDER BY timestamp DESC
    ''', conn)
    conn.close()
    return df


def calculate_metrics(df):
    """计算交易指标"""
    if df.empty:
        return {}
    
    # 按订单ID分组计算盈亏
    order_groups = df.groupby('order_id').agg({
        'pnl': 'sum',
        'fee': 'sum',
        'side': 'first',
        'symbol': 'first',
        'datetime': 'first'
    }).reset_index()
    
    total_trades = len(order_groups)
    winning_trades = len(order_groups[order_groups['pnl'] > 0])
    losing_trades = len(order_groups[order_groups['pnl'] < 0])
    
    total_pnl = order_groups['pnl'].sum()
    total_fee = order_groups['fee'].sum()
    net_pnl = total_pnl - total_fee
    
    win_rate = winning_trades / total_trades * 100 if total_trades > 0 else 0
    
    avg_win = order_groups[order_groups['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
    avg_loss = order_groups[order_groups['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
    
    # 最大连续亏损
    order_groups['is_win'] = order_groups['pnl'] > 0
    max_consecutive_loss = 0
    current_streak = 0
    for is_win in order_groups['is_win']:
        if not is_win:
            current_streak += 1
            max_consecutive_loss = max(max_consecutive_loss, current_streak)
        else:
            current_streak = 0
    
    return {
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'total_pnl': total_pnl,
        'total_fee': total_fee,
        'net_pnl': net_pnl,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'max_consecutive_loss': max_consecutive_loss,
    }


def main():
    st.set_page_config(
        page_title="交易数据面板",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 交易数据面板")
    st.caption("数据来源: OKX 只读API | 自动采集")
    
    # 加载数据
    trades_df = load_trades()
    positions_df = load_positions()
    balance_df = load_balance()
    
    if trades_df.empty:
        st.warning("暂无交易数据，请先运行数据采集")
        st.code("cd dashboard && python fetch_trades.py")
        return
    
    # 计算指标
    metrics = calculate_metrics(trades_df)
    
    # ========== 顶部指标卡片 ==========
    st.subheader("📈 总览")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("总交易笔数", metrics['total_trades'])
    with col2:
        st.metric("胜率", f"{metrics['win_rate']:.1f}%")
    with col3:
        color = "normal" if metrics['net_pnl'] >= 0 else "inverse"
        st.metric("净盈亏 (USDT)", f"{metrics['net_pnl']:.2f}", delta_color=color)
    with col4:
        st.metric("总手续费", f"{metrics['total_fee']:.2f}")
    with col5:
        st.metric("最大连续亏损", f"{metrics['max_consecutive_loss']} 笔")
    
    # ========== 当前持仓 ==========
    st.subheader("💼 当前持仓")
    if not positions_df.empty:
        latest_positions = positions_df.head(10)
        st.dataframe(
            latest_positions[['symbol', 'side', 'contracts', 'entry_price', 'unrealized_pnl', 'timestamp']],
            use_container_width=True
        )
    else:
        st.info("无持仓数据")
    
    # ========== 账户余额 ==========
    st.subheader("💰 账户余额")
    if not balance_df.empty:
        latest_balance = balance_df.head(10)
        fig_balance = px.pie(
            latest_balance, 
            values='total', 
            names='currency',
            title='资产分布'
        )
        st.plotly_chart(fig_balance, use_container_width=True)
    
    # ========== 收益曲线 ==========
    st.subheader("📉 收益曲线")
    if not trades_df.empty:
        # 按订单分组计算累计收益
        order_pnl = trades_df.groupby(['order_id', 'datetime']).agg({
            'pnl': 'sum',
            'fee': 'sum'
        }).reset_index()
        order_pnl['net_pnl'] = order_pnl['pnl'] - order_pnl['fee']
        order_pnl['cumulative_pnl'] = order_pnl['net_pnl'].cumsum()
        order_pnl = order_pnl.sort_values('datetime')
        
        fig_curve = go.Figure()
        fig_curve.add_trace(go.Scatter(
            x=order_pnl['datetime'],
            y=order_pnl['cumulative_pnl'],
            mode='lines+markers',
            name='累计收益',
            line=dict(color='#00d4aa', width=2)
        ))
        fig_curve.update_layout(
            title='累计收益曲线',
            xaxis_title='时间',
            yaxis_title='收益 (USDT)',
            hovermode='x unified'
        )
        st.plotly_chart(fig_curve, use_container_width=True)
    
    # ========== 按币种统计 ==========
    st.subheader("🪙 按币种统计")
    if not trades_df.empty:
        symbol_stats = trades_df.groupby('symbol').agg({
            'pnl': 'sum',
            'fee': 'sum',
            'id': 'count'
        }).rename(columns={'id': 'trade_count'}).reset_index()
        symbol_stats['net_pnl'] = symbol_stats['pnl'] - symbol_stats['fee']
        
        col1, col2 = st.columns(2)
        with col1:
            fig_symbol_pnl = px.bar(
                symbol_stats,
                x='symbol',
                y='net_pnl',
                title='各币种净盈亏',
                color='net_pnl',
                color_continuous_scale=['red', 'green']
            )
            st.plotly_chart(fig_symbol_pnl, use_container_width=True)
        
        with col2:
            fig_symbol_trades = px.pie(
                symbol_stats,
                values='trade_count',
                names='symbol',
                title='各币种交易笔数占比'
            )
            st.plotly_chart(fig_symbol_trades, use_container_width=True)
    
    # ========== 按方向统计 ==========
    st.subheader("📊 按方向统计")
    if not trades_df.empty:
        side_stats = trades_df.groupby('side').agg({
            'pnl': 'sum',
            'fee': 'sum',
            'id': 'count'
        }).rename(columns={'id': 'trade_count'}).reset_index()
        side_stats['net_pnl'] = side_stats['pnl'] - side_stats['fee']
        
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(side_stats, use_container_width=True)
        with col2:
            fig_side = px.bar(
                side_stats,
                x='side',
                y='net_pnl',
                title='多空收益对比',
                color='side',
                color_discrete_map={'buy': '#00d4aa', 'sell': '#ff6b6b'}
            )
            st.plotly_chart(fig_side, use_container_width=True)
    
    # ========== 交易明细 ==========
    st.subheader("📋 交易明细")
    if not trades_df.empty:
        # 筛选
        col1, col2, col3 = st.columns(3)
        with col1:
            symbol_filter = st.multiselect(
                '币种',
                options=trades_df['symbol'].unique(),
                default=trades_df['symbol'].unique()
            )
        with col2:
            side_filter = st.multiselect(
                '方向',
                options=trades_df['side'].unique(),
                default=trades_df['side'].unique()
            )
        with col3:
            date_range = st.date_input(
                '日期范围',
                value=(trades_df['datetime'].min().date(), trades_df['datetime'].max().date())
            )
        
        # 应用筛选
        filtered_df = trades_df[
            (trades_df['symbol'].isin(symbol_filter)) &
            (trades_df['side'].isin(side_filter))
        ]
        
        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df['datetime'].dt.date >= date_range[0]) &
                (filtered_df['datetime'].dt.date <= date_range[1])
            ]
        
        st.dataframe(
            filtered_df[['datetime', 'symbol', 'side', 'price', 'amount', 'cost', 'fee', 'pnl']],
            use_container_width=True,
            height=400
        )
        
        st.caption(f"共 {len(filtered_df)} 条记录")
    
    # ========== 刷新按钮 ==========
    st.sidebar.title("⚙️ 控制")
    if st.sidebar.button("🔄 刷新数据"):
        st.cache_data.clear()
        st.rerun()
    
    st.sidebar.info("""
    **数据更新**
    
    运行以下命令采集最新数据:
    ```bash
    cd dashboard
    python fetch_trades.py
    ```
    """)


if __name__ == '__main__':
    main()
