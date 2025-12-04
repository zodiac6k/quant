"""
NASDAQ Analytics Dashboard
Comprehensive dashboard showing gainers, losers, news analysis, analyst ratings, and visualizations.
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import os
import requests

# Try to import NewsAPI, fallback if not available
try:
    from newsapi import NewsApiClient
    NEWSAPI_AVAILABLE = True
except ImportError:
    NEWSAPI_AVAILABLE = False
    NewsApiClient = None


# Page configuration
st.set_page_config(
    page_title="NASDAQ Analytics Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .positive {
        color: #00cc00;
        font-weight: bold;
    }
    .negative {
        color: #ff0000;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


# Popular NASDAQ stocks for analysis
POPULAR_STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'NFLX',
    'AMD', 'INTC', 'ADBE', 'PYPL', 'CMCSA', 'COST', 'AVGO', 'QCOM',
    'TXN', 'CHTR', 'AMGN', 'ISRG', 'INTU', 'BKNG', 'SBUX', 'ADI'
]


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_data(symbol, period='5d'):
    """Fetch stock data with caching. Returns only DataFrame (serializable)."""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        return data
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return None


def get_ticker(symbol):
    """Get ticker object (not cached, lightweight to create)."""
    return yf.Ticker(symbol)


@st.cache_data(ttl=300)
def get_nasdaq_data(period='5d'):
    """Fetch NASDAQ Composite data."""
    try:
        ticker = yf.Ticker('^IXIC')
        data = ticker.history(period=period)
        return data
    except Exception as e:
        st.error(f"Error fetching NASDAQ data: {e}")
        return None


def calculate_daily_change(data):
    """Calculate daily price change."""
    if data is None or len(data) < 2:
        return None
    
    recent = data.tail(2)
    prev_close = recent.iloc[-2]['Close']
    current_close = recent.iloc[-1]['Close']
    change = current_close - prev_close
    percent_change = (change / prev_close) * 100
    
    return {
        'prev_close': prev_close,
        'current_close': current_close,
        'change': change,
        'percent_change': percent_change
    }


def get_gainers_losers(stocks_list, top_n=10):
    """Get top gainers and losers from a list of stocks."""
    gainers = []
    losers = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, symbol in enumerate(stocks_list):
        status_text.text(f"Fetching data for {symbol}... ({i+1}/{len(stocks_list)})")
        data = get_stock_data(symbol, period='2d')
        
        if data is not None and len(data) >= 2:
            change_data = calculate_daily_change(data)
            if change_data:
                info = {
                    'symbol': symbol,
                    'change': change_data['change'],
                    'percent_change': change_data['percent_change'],
                    'current_price': change_data['current_close']
                }
                
                if change_data['change'] > 0:
                    gainers.append(info)
                else:
                    losers.append(info)
        
        progress_bar.progress((i + 1) / len(stocks_list))
        time.sleep(0.1)  # Rate limiting
    
    progress_bar.empty()
    status_text.empty()
    
    # Sort and return top N
    gainers.sort(key=lambda x: x['percent_change'], reverse=True)
    losers.sort(key=lambda x: x['percent_change'])
    
    return gainers[:top_n], losers[:top_n]


def get_newsapi_client():
    """Initialize NewsAPI client if API key is available."""
    if not NEWSAPI_AVAILABLE:
        return None
    
    try:
        api_key = os.getenv('NEWSAPI_KEY')
        if not api_key:
            try:
                api_key = st.secrets.get('NEWSAPI_KEY', None)
            except:
                pass
        
        if api_key:
            try:
                return NewsApiClient(api_key=api_key)
            except:
                return None
    except:
        pass
    
    return None


def get_news_from_newsapi(symbol, company_name=None):
    """Fetch news from NewsAPI."""
    newsapi = get_newsapi_client()
    if not newsapi:
        return []
    
    try:
        # Try searching by company name first, then symbol
        query = company_name if company_name else symbol
        # Get news from last 7 days
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Search for news
        articles = newsapi.get_everything(
            q=query,
            language='en',
            sort_by='relevancy',
            from_param=from_date,
            page_size=20
        )
        
        if articles and articles.get('status') == 'ok':
            news_list = []
            for article in articles.get('articles', [])[:15]:
                try:
                    pub_date = datetime.strptime(article['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
                    news_list.append({
                        'title': article.get('title', 'N/A'),
                        'publisher': article.get('source', {}).get('name', 'Unknown'),
                        'link': article.get('url', '#'),
                        'date': pub_date.strftime('%Y-%m-%d %H:%M'),
                        'summary': article.get('description', '')[:300] + '...' if article.get('description') and len(article.get('description', '')) > 300 else (article.get('description', '') if article.get('description') else 'N/A')
                    })
                except:
                    continue
            
            return news_list
    except Exception as e:
        # If rate limited or error, return empty
        return []
    
    return []


def get_news_from_yfinance(ticker):
    """Fetch news from yfinance (fallback method)."""
    try:
        news = ticker.news
        if news:
            # Get news from last 7 days
            week_ago = datetime.now() - timedelta(days=7)
            recent_news = []
            
            for item in news[:15]:  # Get top 15 news items
                try:
                    pub_time = item.get('providerPublishTime', 0)
                    if pub_time:
                        pub_date = datetime.fromtimestamp(pub_time)
                        # Include news from last 7 days or if timestamp is 0 (recent)
                        if pub_time == 0 or pub_date.date() >= week_ago.date():
                            recent_news.append({
                                'title': item.get('title', 'N/A'),
                                'publisher': item.get('publisher', 'N/A'),
                                'link': item.get('link', '#'),
                                'date': pub_date.strftime('%Y-%m-%d %H:%M') if pub_time else 'Recent',
                                'summary': item.get('summary', '')[:300] + '...' if item.get('summary') and len(item.get('summary', '')) > 300 else (item.get('summary', '') if item.get('summary') else 'N/A')
                            })
                except:
                    # If date parsing fails, include anyway
                    recent_news.append({
                        'title': item.get('title', 'N/A'),
                        'publisher': item.get('publisher', 'N/A'),
                        'link': item.get('link', '#'),
                        'date': 'Recent',
                        'summary': item.get('summary', '')[:300] + '...' if item.get('summary') and len(item.get('summary', '')) > 300 else (item.get('summary', '') if item.get('summary') else 'N/A')
                    })
            
            return recent_news[:10]  # Return top 10
    except Exception as e:
        return []
    
    return []


def get_news_data(ticker, symbol=None, company_name=None):
    """Fetch news data for a ticker using multiple sources."""
    news_list = []
    sources_used = []
    
    # Try NewsAPI first (better quality)
    if symbol or company_name:
        newsapi_news = get_news_from_newsapi(symbol or '', company_name)
        if newsapi_news:
            news_list.extend(newsapi_news)
            sources_used.append('NewsAPI')
    
    # Fallback to yfinance
    if len(news_list) < 5:
        yfinance_news = get_news_from_yfinance(ticker)
        if yfinance_news:
            # Avoid duplicates
            existing_titles = {n['title'].lower() for n in news_list}
            for news in yfinance_news:
                if news['title'].lower() not in existing_titles:
                    news_list.append(news)
            if yfinance_news:
                sources_used.append('Yahoo Finance')
    
    # Remove duplicates and sort by date
    seen_titles = set()
    unique_news = []
    for news in news_list:
        title_lower = news['title'].lower()
        if title_lower not in seen_titles:
            seen_titles.add(title_lower)
            unique_news.append(news)
    
    # Sort by date (most recent first)
    try:
        unique_news.sort(key=lambda x: x['date'], reverse=True)
    except:
        pass
    
    return unique_news[:15], sources_used  # Return top 15 and sources used


def extract_reasons_from_news(news_list):
    """Extract potential reasons for price movement from news."""
    reasons = []
    keywords = {
        'positive': ['earnings', 'beat', 'surprise', 'upgrade', 'buy', 'growth', 'profit', 'revenue', 'strong'],
        'negative': ['miss', 'downgrade', 'sell', 'loss', 'decline', 'weak', 'concern', 'warning', 'cut']
    }
    
    for news_item in news_list[:5]:
        title_lower = news_item['title'].lower()
        summary_lower = news_item.get('summary', '').lower()
        text = title_lower + ' ' + summary_lower
        
        sentiment = 'neutral'
        if any(keyword in text for keyword in keywords['positive']):
            sentiment = 'positive'
        elif any(keyword in text for keyword in keywords['negative']):
            sentiment = 'negative'
        
        reasons.append({
            'title': news_item['title'],
            'sentiment': sentiment,
            'publisher': news_item['publisher']
        })
    
    return reasons


def get_analyst_ratings(ticker):
    """Get analyst recommendations."""
    try:
        recommendations = ticker.recommendations
        if recommendations is not None and len(recommendations) > 0:
            # Get most recent recommendations
            latest = recommendations.tail(20)
            
            # Check available columns
            available_cols = latest.columns.tolist()
            
            # Try different possible column names for ratings
            rating_col = None
            for col in ['To Grade', 'toGrade', 'ToGrade', 'Rating', 'rating']:
                if col in available_cols:
                    rating_col = col
                    break
            
            if rating_col:
                # Count ratings
                rating_counts = latest[rating_col].value_counts().to_dict()
            else:
                # If no rating column, try to infer from other columns
                rating_counts = {}
                if 'Action' in available_cols:
                    rating_counts = latest['Action'].value_counts().to_dict()
            
            # Get detailed recommendations
            detailed = []
            for idx, row in latest.iterrows():
                rec_dict = {
                    'Date': idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx),
                    'Firm': row.get('Firm', 'N/A') if 'Firm' in available_cols else 'N/A',
                }
                
                # Add rating columns if available
                if 'From Grade' in available_cols or 'fromGrade' in available_cols:
                    rec_dict['From'] = row.get('From Grade', row.get('fromGrade', 'N/A'))
                if rating_col:
                    rec_dict['To'] = row.get(rating_col, 'N/A')
                if 'Action' in available_cols:
                    rec_dict['Action'] = row.get('Action', 'N/A')
                
                detailed.append(rec_dict)
            
            return rating_counts, detailed
    except Exception as e:
        # Try alternative method using info
        try:
            info = ticker.info
            # Get recommendation data from info
            recommendation_key = info.get('recommendationKey', '')
            recommendation_mean = info.get('recommendationMean', 0)
            
            if recommendation_key:
                # Map recommendation key to readable format
                rating_map = {
                    'strong_buy': 'Strong Buy',
                    'buy': 'Buy',
                    'hold': 'Hold',
                    'sell': 'Sell',
                    'strong_sell': 'Strong Sell'
                }
                rating_name = rating_map.get(recommendation_key, recommendation_key.title())
                return {rating_name: 1}, [{'Date': 'Current', 'Rating': rating_name, 'Mean Score': f"{recommendation_mean:.2f}"}]
        except:
            pass
    
    return {}, []


def calculate_weekly_forecast(data, news_reasons, ticker):
    """Calculate expected price change in one week based on analytics."""
    if data is None or len(data) < 5:
        return None, "Insufficient data for forecast"
    
    try:
        # Get more historical data for better analysis
        extended_data = data.tail(10) if len(data) >= 10 else data
        
        # Calculate momentum
        recent_prices = extended_data['Close'].tolist()
        momentum = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
        
        # Moving averages
        ma_5 = extended_data.tail(5)['Close'].mean()
        ma_10 = extended_data['Close'].mean() if len(extended_data) >= 10 else ma_5
        current_price = recent_prices[-1]
        
        # Volume trend
        recent_volumes = extended_data.tail(5)['Volume'].tolist()
        volume_trend = (recent_volumes[-1] - recent_volumes[0]) / recent_volumes[0] if recent_volumes[0] > 0 else 0
        
        # News sentiment score
        positive_news = sum(1 for r in news_reasons if r['sentiment'] == 'positive')
        negative_news = sum(1 for r in news_reasons if r['sentiment'] == 'negative')
        news_score = (positive_news - negative_news) / max(len(news_reasons), 1) if news_reasons else 0
        
        # Volatility
        volatility = extended_data['Close'].std() / extended_data['Close'].mean()
        
        # Try to get analyst target price
        target_price = None
        try:
            info = ticker.info
            target_price = info.get('targetMeanPrice', info.get('targetHighPrice', None))
        except:
            pass
        
        # Calculate forecast factors
        momentum_factor = momentum * 0.3  # 30% weight on momentum
        ma_factor = ((current_price - ma_5) / ma_5 * 100) * 0.2  # 20% weight on MA position
        news_factor = news_score * 2  # News sentiment impact
        volume_factor = volume_trend * 0.5  # Volume trend impact
        
        # Base forecast on weekly momentum (extrapolate 5-day momentum to 7 days)
        weekly_forecast_pct = (momentum_factor + ma_factor + news_factor + volume_factor) * (7/5)
        
        # If we have target price, incorporate it
        if target_price and target_price > 0:
            target_pct = ((target_price - current_price) / current_price * 100) * 0.3
            weekly_forecast_pct = weekly_forecast_pct * 0.7 + target_pct * 0.3
        
        # Cap forecast to reasonable range (-15% to +15%)
        weekly_forecast_pct = max(-15, min(15, weekly_forecast_pct))
        
        forecast_price = current_price * (1 + weekly_forecast_pct / 100)
        price_change = forecast_price - current_price
        
        # Generate confidence level
        confidence_factors = []
        if abs(momentum) > 1:
            confidence_factors.append("Strong momentum")
        if abs(current_price - ma_5) / ma_5 > 0.02:
            confidence_factors.append("Clear trend")
        if len(news_reasons) >= 3:
            confidence_factors.append("News coverage")
        if target_price:
            confidence_factors.append("Analyst targets")
        
        confidence = "High" if len(confidence_factors) >= 3 else "Medium" if len(confidence_factors) >= 2 else "Low"
        
        return {
            'current_price': current_price,
            'forecast_price': forecast_price,
            'price_change': price_change,
            'percent_change': weekly_forecast_pct,
            'confidence': confidence,
            'factors': confidence_factors,
            'target_price': target_price
        }, None
        
    except Exception as e:
        return None, f"Error calculating forecast: {e}"


def calculate_price_insights(data, news_reasons):
    """Generate insights on possible price increases."""
    insights = []
    
    if data is None or len(data) < 5:
        return ["Insufficient data for analysis"]
    
    # Technical indicators
    recent_data = data.tail(5)
    current_price = recent_data.iloc[-1]['Close']
    ma_5 = recent_data['Close'].mean()
    
    # Volume analysis
    avg_volume = recent_data['Volume'].mean()
    current_volume = recent_data.iloc[-1]['Volume']
    
    # Price trend
    price_trend = 'upward' if current_price > ma_5 else 'downward'
    
    # News sentiment
    positive_news = sum(1 for r in news_reasons if r['sentiment'] == 'positive')
    negative_news = sum(1 for r in news_reasons if r['sentiment'] == 'negative')
    
    insights.append(f"📊 **Price Trend**: {price_trend.capitalize()} trend detected")
    insights.append(f"📈 **Moving Average**: Current price is {'above' if current_price > ma_5 else 'below'} 5-day average")
    
    if current_volume > avg_volume * 1.2:
        insights.append(f"📊 **Volume**: High trading volume detected ({(current_volume/avg_volume*100):.1f}% above average)")
    
    if positive_news > negative_news:
        insights.append(f"📰 **News Sentiment**: Positive news flow ({positive_news} positive vs {negative_news} negative)")
    elif negative_news > positive_news:
        insights.append(f"📰 **News Sentiment**: Negative news flow ({negative_news} negative vs {positive_news} positive)")
    else:
        insights.append(f"📰 **News Sentiment**: Mixed news flow")
    
    # Volatility
    volatility = recent_data['Close'].std() / recent_data['Close'].mean() * 100
    if volatility > 3:
        insights.append(f"⚡ **Volatility**: High volatility detected ({volatility:.2f}%)")
    
    return insights


def create_comparison_chart(security_data, nasdaq_data, security_symbol):
    """Create bar chart comparing security vs NASDAQ."""
    if security_data is None or nasdaq_data is None:
        return None
    
    # Calculate daily changes for both
    security_changes = []
    nasdaq_changes = []
    dates = []
    
    # Get last 5 days of data
    sec_recent = security_data.tail(5)
    nas_recent = nasdaq_data.tail(5)
    
    for i in range(1, len(sec_recent)):
        sec_prev = sec_recent.iloc[i-1]['Close']
        sec_curr = sec_recent.iloc[i]['Close']
        sec_change = ((sec_curr - sec_prev) / sec_prev) * 100
        
        nas_prev = nas_recent.iloc[i-1]['Close']
        nas_curr = nas_recent.iloc[i]['Close']
        nas_change = ((nas_curr - nas_prev) / nas_prev) * 100
        
        security_changes.append(sec_change)
        nasdaq_changes.append(nas_change)
        dates.append(sec_recent.iloc[i].name.strftime('%Y-%m-%d'))
    
    # Create DataFrame
    df = pd.DataFrame({
        'Date': dates,
        security_symbol: security_changes,
        'NASDAQ': nasdaq_changes
    })
    
    # Create bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name=security_symbol,
        x=df['Date'],
        y=df[security_symbol],
        marker_color='#1f77b4'
    ))
    
    fig.add_trace(go.Bar(
        name='NASDAQ',
        x=df['Date'],
        y=df['NASDAQ'],
        marker_color='#ff7f0e'
    ))
    
    fig.update_layout(
        title=f'Daily Percentage Change: {security_symbol} vs NASDAQ',
        xaxis_title='Date',
        yaxis_title='Percentage Change (%)',
        barmode='group',
        height=400,
        hovermode='x unified'
    )
    
    return fig


def show_stock_summary():
    """Display summary of multiple stocks with forecasts and confidence levels."""
    st.header("📊 Stock Summary & Forecasts")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        num_stocks = st.slider("Number of Stocks", 5, len(POPULAR_STOCKS), 10)
    with col2:
        confidence_filter = st.selectbox(
            "Filter by Confidence",
            ["All", "High", "Medium", "Low"],
            index=0
        )
    with col3:
        sort_by = st.selectbox(
            "Sort By",
            ["Confidence", "Forecast %", "Current Price", "Symbol"],
            index=0
        )
    
    # Select stocks to analyze
    stocks_to_analyze = POPULAR_STOCKS[:num_stocks]
    
    if st.button("Analyze Stocks", type="primary"):
        with st.spinner("Analyzing stocks and generating forecasts..."):
            stock_summaries = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, symbol in enumerate(stocks_to_analyze):
                status_text.text(f"Analyzing {symbol}... ({i+1}/{len(stocks_to_analyze)})")
                
                try:
                    stock_data = get_stock_data(symbol, period='10d')
                    if stock_data is not None and len(stock_data) >= 5:
                        ticker = get_ticker(symbol)
                        # Get company name for better news search
                        try:
                            info = ticker.info
                            company_name = info.get('longName', symbol)
                        except:
                            company_name = symbol
                        
                        news_list, sources_used = get_news_data(ticker, symbol=symbol, company_name=company_name)
                        reasons = extract_reasons_from_news(news_list)
                        forecast, forecast_error = calculate_weekly_forecast(stock_data, reasons, ticker)
                        
                        if forecast:
                            change_data = calculate_daily_change(stock_data)
                            
                            # Get company name
                            try:
                                info = ticker.info
                                company_name = info.get('longName', symbol)
                            except:
                                company_name = symbol
                            
                            stock_summaries.append({
                                'Symbol': symbol,
                                'Company': company_name,
                                'Current Price': stock_data.iloc[-1]['Close'],
                                'Daily Change %': change_data['percent_change'] if change_data else 0,
                                'Forecast Price': forecast['forecast_price'],
                                'Forecast Change %': forecast['percent_change'],
                                'Price Change': forecast['price_change'],
                                'Confidence': forecast['confidence'],
                                'Factors Count': len(forecast['factors']),
                                'Target Price': forecast.get('target_price', None)
                            })
                except Exception as e:
                    st.warning(f"Error analyzing {symbol}: {e}")
                
                progress_bar.progress((i + 1) / len(stocks_to_analyze))
                time.sleep(0.1)
            
            progress_bar.empty()
            status_text.empty()
            
            if stock_summaries:
                df = pd.DataFrame(stock_summaries)
                
                # Apply confidence filter
                if confidence_filter != "All":
                    df = df[df['Confidence'] == confidence_filter]
                
                # Sort
                if sort_by == "Confidence":
                    confidence_order = {"High": 3, "Medium": 2, "Low": 1}
                    df['Confidence_Order'] = df['Confidence'].map(confidence_order)
                    df = df.sort_values('Confidence_Order', ascending=False).drop('Confidence_Order', axis=1)
                elif sort_by == "Forecast %":
                    df = df.sort_values('Forecast Change %', ascending=False)
                elif sort_by == "Current Price":
                    df = df.sort_values('Current Price', ascending=False)
                else:
                    df = df.sort_values('Symbol')
                
                # Display summary statistics
                st.markdown("### 📈 Summary Statistics")
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                
                with stat_col1:
                    high_conf = len(df[df['Confidence'] == 'High'])
                    st.metric("High Confidence", high_conf)
                
                with stat_col2:
                    avg_forecast = df['Forecast Change %'].mean()
                    st.metric("Avg Forecast %", f"{avg_forecast:.2f}%")
                
                with stat_col3:
                    positive_forecasts = len(df[df['Forecast Change %'] > 0])
                    st.metric("Positive Forecasts", positive_forecasts)
                
                with stat_col4:
                    total_stocks = len(df)
                    st.metric("Total Stocks", total_stocks)
                
                st.markdown("---")
                
                # Visualizations
                viz_tab1, viz_tab2, viz_tab3 = st.tabs(["📊 Forecast Overview", "📈 Confidence Distribution", "💰 Price Forecasts"])
                
                with viz_tab1:
                    # Forecast scatter plot
                    fig = px.scatter(
                        df,
                        x='Current Price',
                        y='Forecast Price',
                        size='Forecast Change %',
                        color='Confidence',
                        hover_data=['Symbol', 'Company', 'Forecast Change %'],
                        title='Current Price vs Forecasted Price',
                        color_discrete_map={
                            'High': '#00cc00',
                            'Medium': '#ffaa00',
                            'Low': '#ff6666'
                        },
                        size_max=20
                    )
                    # Add diagonal line
                    max_price = max(df['Current Price'].max(), df['Forecast Price'].max())
                    min_price = min(df['Current Price'].min(), df['Forecast Price'].min())
                    fig.add_trace(go.Scatter(
                        x=[min_price, max_price],
                        y=[min_price, max_price],
                        mode='lines',
                        line=dict(color='gray', dash='dash'),
                        name='No Change Line',
                        showlegend=False
                    ))
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, use_container_width=True)
                
                with viz_tab2:
                    # Confidence distribution
                    conf_col1, conf_col2 = st.columns(2)
                    
                    with conf_col1:
                        # Pie chart
                        conf_counts = df['Confidence'].value_counts()
                        fig = px.pie(
                            values=conf_counts.values,
                            names=conf_counts.index,
                            title="Confidence Level Distribution",
                            color_discrete_map={
                                'High': '#00cc00',
                                'Medium': '#ffaa00',
                                'Low': '#ff6666'
                            }
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with conf_col2:
                        # Bar chart
                        fig = px.bar(
                            x=conf_counts.index,
                            y=conf_counts.values,
                            title="Stocks by Confidence Level",
                            labels={'x': 'Confidence', 'y': 'Count'},
                            color=conf_counts.index,
                            color_discrete_map={
                                'High': '#00cc00',
                                'Medium': '#ffaa00',
                                'Low': '#ff6666'
                            }
                        )
                        fig.update_layout(showlegend=False, height=400)
                        st.plotly_chart(fig, use_container_width=True)
                
                with viz_tab3:
                    # Forecast bar chart
                    df_sorted = df.sort_values('Forecast Change %', ascending=True)
                    fig = go.Figure()
                    
                    colors = []
                    for conf in df_sorted['Confidence']:
                        if conf == 'High':
                            colors.append('#00cc00')
                        elif conf == 'Medium':
                            colors.append('#ffaa00')
                        else:
                            colors.append('#ff6666')
                    
                    fig.add_trace(go.Bar(
                        y=df_sorted['Symbol'],
                        x=df_sorted['Forecast Change %'],
                        orientation='h',
                        marker=dict(color=colors),
                        text=[f"{x:.2f}%" for x in df_sorted['Forecast Change %']],
                        textposition='auto',
                        hovertemplate='<b>%{y}</b><br>Forecast: %{x:.2f}%<br>Confidence: ' + df_sorted['Confidence'] + '<extra></extra>'
                    ))
                    
                    fig.update_layout(
                        title='7-Day Forecast by Stock (Sorted)',
                        xaxis_title='Forecast Change (%)',
                        yaxis_title='Stock Symbol',
                        height=600
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                # Detailed table
                st.markdown("### 📋 Detailed Stock Forecasts")
                
                # Format table with color coding
                def color_confidence(val):
                    if val == 'High':
                        return 'background-color: #d4edda; color: #155724;'
                    elif val == 'Medium':
                        return 'background-color: #fff3cd; color: #856404;'
                    else:
                        return 'background-color: #f8d7da; color: #721c24;'
                
                def color_forecast(val):
                    if val > 0:
                        return 'background-color: #d4edda; color: #155724;'
                    else:
                        return 'background-color: #f8d7da; color: #721c24;'
                
                # Prepare display dataframe
                display_df = df.copy()
                display_df['Current Price'] = display_df['Current Price'].apply(lambda x: f"${x:,.2f}")
                display_df['Forecast Price'] = display_df['Forecast Price'].apply(lambda x: f"${x:,.2f}")
                display_df['Price Change'] = display_df['Price Change'].apply(lambda x: f"${x:,.2f}")
                display_df['Daily Change %'] = display_df['Daily Change %'].apply(lambda x: f"{x:+.2f}%")
                display_df['Forecast Change %'] = display_df['Forecast Change %'].apply(lambda x: f"{x:+.2f}%")
                if 'Target Price' in display_df.columns:
                    display_df['Target Price'] = display_df['Target Price'].apply(
                        lambda x: f"${x:,.2f}" if pd.notna(x) and x is not None and x != 0 else "N/A"
                    )
                
                # Apply styling
                styled_df = display_df.style.applymap(
                    color_confidence,
                    subset=['Confidence']
                ).applymap(
                    lambda x: color_forecast(float(x.replace('$', '').replace(',', ''))) if '$' in str(x) else '',
                    subset=['Price Change']
                )
                
                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Forecast Data (CSV)",
                    data=csv,
                    file_name=f"stock_forecasts_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No stock forecasts could be generated. Please try again.")


def main():
    """Main dashboard function."""
    st.markdown('<h1 class="main-header">📈 NASDAQ Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.selectbox(
        "Select Page",
        ["Market Overview", "Stock Analysis", "Stock Summary", "Gainers & Losers"]
    )
    
    if page == "Market Overview":
        show_market_overview()
    elif page == "Stock Analysis":
        show_stock_analysis()
    elif page == "Stock Summary":
        show_stock_summary()
    elif page == "Gainers & Losers":
        show_gainers_losers()


def show_market_overview():
    """Display market overview."""
    st.header("📊 NASDAQ Market Overview")
    
    nasdaq_data = get_nasdaq_data(period='5d')
    
    if nasdaq_data is not None and len(nasdaq_data) >= 2:
        change_data = calculate_daily_change(nasdaq_data)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current Close", f"${nasdaq_data.iloc[-1]['Close']:,.2f}")
        
        with col2:
            change_color = "normal" if change_data['change'] >= 0 else "inverse"
            st.metric(
                "Daily Change",
                f"${change_data['change']:,.2f}",
                f"{change_data['percent_change']:.2f}%"
            )
        
        with col3:
            st.metric("High", f"${nasdaq_data.iloc[-1]['High']:,.2f}")
        
        with col4:
            st.metric("Low", f"${nasdaq_data.iloc[-1]['Low']:,.2f}")
        
        # Chart
        st.subheader("NASDAQ 5-Day Trend")
        fig = px.line(
            nasdaq_data.reset_index(),
            x='Date',
            y='Close',
            title='NASDAQ Composite - Last 5 Days'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)


def show_stock_analysis():
    """Display detailed stock analysis."""
    st.header("🔍 Stock Analysis")
    
    # Stock selector
    selected_stock = st.selectbox(
        "Select a Stock",
        options=POPULAR_STOCKS,
        index=0
    )
    
    if selected_stock:
        stock_data = get_stock_data(selected_stock, period='10d')
        nasdaq_data = get_nasdaq_data(period='10d')
        
        if stock_data is not None:
            # Get ticker for additional info
            ticker = get_ticker(selected_stock)
            
            # Get stock info
            try:
                info = ticker.info
                company_name = info.get('longName', selected_stock)
                st.subheader(f"{company_name} ({selected_stock})")
            except:
                st.subheader(f"{selected_stock}")
            
            # Key metrics with better styling
            change_data = calculate_daily_change(stock_data)
            
            # Main metrics row
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Current Price", f"${stock_data.iloc[-1]['Close']:,.2f}")
            
            with col2:
                if change_data:
                    delta_color = "normal" if change_data['change'] >= 0 else "inverse"
                    st.metric(
                        "Daily Change",
                        f"${change_data['change']:,.2f}",
                        f"{change_data['percent_change']:.2f}%",
                        delta_color=delta_color
                    )
            
            with col3:
                st.metric("Volume", f"{stock_data.iloc[-1]['Volume']:,.0f}")
            
            with col4:
                try:
                    market_cap = ticker.info.get('marketCap', 0)
                    if market_cap:
                        st.metric("Market Cap", f"${market_cap/1e9:.2f}B")
                    else:
                        st.metric("Market Cap", "N/A")
                except:
                    st.metric("Market Cap", "N/A")
            
            with col5:
                try:
                    pe_ratio = ticker.info.get('trailingPE', None)
                    if pe_ratio:
                        st.metric("P/E Ratio", f"{pe_ratio:.2f}")
                    else:
                        st.metric("P/E Ratio", "N/A")
                except:
                    st.metric("P/E Ratio", "N/A")
            
            # Comparison chart
            st.subheader("📊 Comparison: Stock vs NASDAQ")
            comparison_fig = create_comparison_chart(stock_data, nasdaq_data, selected_stock)
            if comparison_fig:
                st.plotly_chart(comparison_fig, use_container_width=True)
            
            # Tabs for different analyses
            tab1, tab2, tab3, tab4 = st.tabs(["News Analysis", "Analyst Ratings", "Price Insights", "Historical Data"])
            
            with tab1:
                st.subheader("📰 News Flow Analysis")
                
                # Get company name for better news search
                try:
                    info = ticker.info
                    company_name = info.get('longName', selected_stock)
                except:
                    company_name = selected_stock
                
                news_list, sources_used = get_news_data(ticker, symbol=selected_stock, company_name=company_name)
                
                if news_list:
                    sources_text = " & ".join(sources_used) if sources_used else "Multiple sources"
                    st.success(f"Found {len(news_list)} recent news items from the past week (Source: {sources_text})")
                    
                    reasons = extract_reasons_from_news(news_list)
                    
                    if reasons:
                        st.markdown("#### 🎯 Potential Reasons for Price Movement")
                        for reason in reasons:
                            sentiment_emoji = "🟢" if reason['sentiment'] == 'positive' else "🔴" if reason['sentiment'] == 'negative' else "🟡"
                            sentiment_color = "#00cc00" if reason['sentiment'] == 'positive' else "#ff0000" if reason['sentiment'] == 'negative' else "#ffaa00"
                            st.markdown(f"""
                            <div style='padding: 12px; margin: 8px 0; background-color: #f9f9f9; border-left: 4px solid {sentiment_color}; border-radius: 4px;'>
                                <strong>{sentiment_emoji} {reason['title']}</strong><br>
                                <small style='color: #666;'>{reason['publisher']}</small>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.markdown("#### 📰 Recent News Headlines")
                    for i, news in enumerate(news_list[:8], 1):
                        with st.expander(f"{i}. {news['title']} - {news['publisher']} ({news['date']})"):
                            st.write(f"[Read full article]({news['link']})")
                            if news['summary'] != 'N/A':
                                st.write(news['summary'])
                else:
                    st.warning("No recent news found for this stock.")
                    
                    # Show API setup instructions if NewsAPI not configured (in collapsible section)
                    newsapi = get_newsapi_client()
                    if not newsapi:
                        with st.expander("💡 Want better news coverage? Set up NewsAPI (Optional)", expanded=False):
                            st.markdown("""
                            **Get more comprehensive news coverage with a free NewsAPI account:**
                            
                            ### For Local Development:
                            1. **Get Free API Key**: Visit https://newsapi.org/register
                            2. **Set API Key**: Create `.streamlit/secrets.toml`:
                               ```toml
                               NEWSAPI_KEY = "your_api_key_here"
                               ```
                            
                            ### For Streamlit Cloud:
                            1. Go to your app settings on [share.streamlit.io](https://share.streamlit.io)
                            2. Click **"Secrets"** in the sidebar
                            3. Add your API key:
                               ```toml
                               NEWSAPI_KEY = "your_api_key_here"
                               ```
                            4. The app will automatically redeploy
                            
                            **Free Tier**: 100 requests/day
                            
                            *Note: The dashboard works fine without NewsAPI using Yahoo Finance as a fallback.*
                            """)
                    else:
                        st.write("**Possible reasons:**")
                        st.write("- Limited news coverage for this stock")
                        st.write("- No recent news updates in the past week")
                        st.write("- News may be filtered out")
            
            with tab2:
                st.subheader("📊 Analyst Ratings & Recommendations")
                rating_counts, detailed_ratings = get_analyst_ratings(ticker)
                
                if rating_counts and len(rating_counts) > 0:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### Rating Summary")
                        for rating, count in sorted(rating_counts.items(), key=lambda x: x[1], reverse=True):
                            # Color code ratings
                            if 'buy' in rating.lower() or 'strong buy' in rating.lower():
                                color = "#00cc00"
                            elif 'sell' in rating.lower() or 'strong sell' in rating.lower():
                                color = "#ff0000"
                            else:
                                color = "#ffaa00"
                            
                            st.markdown(f"""
                            <div style='padding: 10px; margin: 5px 0; background-color: #f9f9f9; border-left: 4px solid {color}; border-radius: 4px;'>
                                <strong>{rating}</strong>: {count} analyst(s)
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with col2:
                        # Pie chart of ratings
                        if rating_counts:
                            fig = px.pie(
                                values=list(rating_counts.values()),
                                names=list(rating_counts.keys()),
                                title="Analyst Rating Distribution",
                                color_discrete_sequence=px.colors.qualitative.Set3
                            )
                            fig.update_traces(textposition='inside', textinfo='percent+label')
                            st.plotly_chart(fig, use_container_width=True)
                    
                    if detailed_ratings and len(detailed_ratings) > 0:
                        st.markdown("#### Recent Recommendations")
                        df_ratings = pd.DataFrame(detailed_ratings)
                        st.dataframe(df_ratings, use_container_width=True, hide_index=True)
                else:
                    st.info("No detailed analyst ratings available for this stock.")
                    st.write("**Note**: Some stocks may not have publicly available analyst recommendations, or the data format may differ.")
                    
                    # Try to show any available info
                    try:
                        info = ticker.info
                        if 'recommendationKey' in info:
                            st.write(f"**Overall Recommendation**: {info.get('recommendationKey', 'N/A').title()}")
                        if 'recommendationMean' in info:
                            st.write(f"**Recommendation Score**: {info.get('recommendationMean', 'N/A')} (Lower is better)")
                    except:
                        pass
            
            with tab3:
                st.subheader("💡 Price Insights & Weekly Forecast")
                
                # Confidence Filter
                confidence_filter = st.selectbox(
                    "Filter by Confidence Level",
                    ["All", "High", "Medium", "Low"],
                    index=0,
                    key="confidence_filter"
                )
                
                # Weekly Forecast Card
                # Get company name for better news search
                try:
                    info = ticker.info
                    company_name = info.get('longName', selected_stock)
                except:
                    company_name = selected_stock
                
                news_list, sources_used = get_news_data(ticker, symbol=selected_stock, company_name=company_name)
                reasons = extract_reasons_from_news(news_list)
                forecast, forecast_error = calculate_weekly_forecast(stock_data, reasons, ticker)
                
                # Apply confidence filter - show info message
                if forecast:
                    if confidence_filter != "All":
                        if forecast['confidence'] == confidence_filter:
                            st.success(f"✓ Showing forecast with **{confidence_filter}** confidence")
                        else:
                            st.warning(f"⚠️ Current forecast confidence is **'{forecast['confidence']}'**, but filter is set to **'{confidence_filter}'**. Showing forecast anyway - change filter to match.")
                    else:
                        st.info(f"💡 Current forecast confidence: **{forecast['confidence']}**. Use filter above to focus on specific levels.")
                
                if forecast:
                    st.markdown("### 📈 7-Day Price Forecast")
                    forecast_col1, forecast_col2, forecast_col3 = st.columns(3)
                    
                    with forecast_col1:
                        st.markdown(f"""
                        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;'>
                            <h3 style='color: #1f77b4; margin: 0;'>Current Price</h3>
                            <h2 style='margin: 10px 0;'>${forecast['current_price']:,.2f}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with forecast_col2:
                        forecast_color = "#00cc00" if forecast['price_change'] >= 0 else "#ff0000"
                        arrow = "▲" if forecast['price_change'] >= 0 else "▼"
                        st.markdown(f"""
                        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;'>
                            <h3 style='color: #1f77b4; margin: 0;'>Forecasted Price</h3>
                            <h2 style='margin: 10px 0; color: {forecast_color};'>{arrow} ${forecast['forecast_price']:,.2f}</h2>
                            <p style='margin: 5px 0; color: {forecast_color}; font-size: 18px;'>{arrow} {abs(forecast['percent_change']):.2f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with forecast_col3:
                        confidence_color = "#00cc00" if forecast['confidence'] == "High" else "#ffaa00" if forecast['confidence'] == "Medium" else "#ff6666"
                        st.markdown(f"""
                        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;'>
                            <h3 style='color: #1f77b4; margin: 0;'>Confidence</h3>
                            <h2 style='margin: 10px 0; color: {confidence_color};'>{forecast['confidence']}</h2>
                            <p style='margin: 5px 0; font-size: 14px;'>Based on {len(forecast['factors'])} factors</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    # Forecast details
                    st.markdown("#### Forecast Analysis")
                    forecast_details_col1, forecast_details_col2 = st.columns(2)
                    
                    with forecast_details_col1:
                        st.write("**Expected Change:**")
                        st.write(f"- Price Change: ${forecast['price_change']:,.2f}")
                        st.write(f"- Percentage: {forecast['percent_change']:+.2f}%")
                        if forecast['target_price']:
                            st.write(f"- Analyst Target: ${forecast['target_price']:,.2f}")
                    
                    with forecast_details_col2:
                        st.write("**Confidence Factors:**")
                        for factor in forecast['factors']:
                            st.write(f"- ✓ {factor}")
                    
                    st.info("⚠️ **Disclaimer**: This forecast is based on technical analysis and historical patterns. Past performance does not guarantee future results. Always do your own research and consult with financial advisors.")
                
                elif forecast_error:
                    st.warning(f"Could not generate forecast: {forecast_error}")
                
                st.markdown("---")
                
                # Technical Insights
                st.markdown("#### 📊 Technical Analysis")
                insights = calculate_price_insights(stock_data, reasons)
                
                for insight in insights:
                    st.markdown(f"<div style='padding: 10px; margin: 5px 0; background-color: #f9f9f9; border-left: 4px solid #1f77b4;'>{insight}</div>", unsafe_allow_html=True)
                
                # Additional technical analysis
                st.markdown("#### 📈 Technical Indicators")
                recent_5 = stock_data.tail(5)
                ma_5 = recent_5['Close'].mean()
                current = stock_data.iloc[-1]['Close']
                
                tech_col1, tech_col2 = st.columns(2)
                with tech_col1:
                    st.write(f"- **5-Day Moving Average**: ${ma_5:,.2f}")
                    st.write(f"- **Current vs MA5**: {'Above' if current > ma_5 else 'Below'} by {abs((current - ma_5) / ma_5 * 100):.2f}%")
                
                with tech_col2:
                    if len(stock_data) >= 10:
                        ma_10 = stock_data.tail(10)['Close'].mean()
                        st.write(f"- **10-Day Moving Average**: ${ma_10:,.2f}")
                        st.write(f"- **52-Week Range**: Check historical data tab")
            
            with tab4:
                st.subheader("📈 Historical Data")
                st.dataframe(stock_data.tail(10), use_container_width=True)


def show_gainers_losers():
    """Display gainers and losers."""
    st.header("🏆 Top Gainers & Losers")
    
    num_stocks = st.sidebar.slider("Number of stocks to analyze", 10, 50, 20)
    top_n = st.sidebar.slider("Top N to display", 5, 20, 10)
    
    if st.button("Analyze Gainers & Losers"):
        with st.spinner("Fetching data for multiple stocks..."):
            stocks_to_analyze = POPULAR_STOCKS[:num_stocks]
            gainers, losers = get_gainers_losers(stocks_to_analyze, top_n)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🟢 Top Gainers")
            if gainers:
                gainers_df = pd.DataFrame(gainers)
                gainers_df['change'] = gainers_df['change'].apply(lambda x: f"${x:,.2f}")
                gainers_df['percent_change'] = gainers_df['percent_change'].apply(lambda x: f"{x:.2f}%")
                gainers_df['current_price'] = gainers_df['current_price'].apply(lambda x: f"${x:,.2f}")
                gainers_df.columns = ['Symbol', 'Change', 'Change %', 'Price']
                st.dataframe(gainers_df, use_container_width=True, hide_index=True)
            else:
                st.info("No gainers found.")
        
        with col2:
            st.subheader("🔴 Top Losers")
            if losers:
                losers_df = pd.DataFrame(losers)
                losers_df['change'] = losers_df['change'].apply(lambda x: f"${x:,.2f}")
                losers_df['percent_change'] = losers_df['percent_change'].apply(lambda x: f"{x:.2f}%")
                losers_df['current_price'] = losers_df['current_price'].apply(lambda x: f"${x:,.2f}")
                losers_df.columns = ['Symbol', 'Change', 'Change %', 'Price']
                st.dataframe(losers_df, use_container_width=True, hide_index=True)
            else:
                st.info("No losers found.")
        
        # Contributors to movement
        if gainers or losers:
            st.subheader("📊 Contributors to NASDAQ Movement")
            
            # Calculate weighted contribution (simplified)
            all_stocks = gainers + losers
            total_positive = sum(g['percent_change'] for g in gainers)
            total_negative = sum(abs(l['percent_change']) for l in losers)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Positive Contribution", f"{total_positive:.2f}%")
            with col2:
                st.metric("Total Negative Contribution", f"{total_negative:.2f}%")
            
            # Bar chart of top contributors
            if all_stocks:
                contributors_df = pd.DataFrame(all_stocks[:10])
                fig = px.bar(
                    contributors_df,
                    x='symbol',
                    y='percent_change',
                    title='Top Contributors to Market Movement',
                    color='percent_change',
                    color_continuous_scale=['red', 'green']
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
