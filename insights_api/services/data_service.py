# insights_api/services/data_service.py
import json
import os
from datetime import datetime, timedelta

import requests
import yfinance as yf
from dashboard.models import DataCollectionTask, NewsArticle, Symbol


class DataCollectionService:
    def collect_market_data(self, task_id, symbols=None, use_cached=True):
        """Collect market data for specified symbols"""
        task = DataCollectionTask.objects.get(id=task_id)
        task.status = 'running'
        task.save()
        
        if not symbols:
            symbols = Symbol.objects.values_list('ticker', flat=True)[:20]
        
        try:
            # Implementation using yfinance
            result = {"processed_symbols": []}
            for ticker in symbols:
                # Get stock data
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1mo")
                
                # Update symbol info if available
                try:
                    info = stock.info
                    symbol = Symbol.objects.get(ticker=ticker)
                    if 'marketCap' in info:
                        symbol.market_cap = info['marketCap']
                    symbol.save()
                    result["processed_symbols"].append(ticker)
                except:
                    pass
            
            task.status = 'completed'
            task.result = result
            task.completed_at = datetime.now()
            task.save()
            return result
        except Exception as e:
            task.status = 'failed'
            task.error_message = str(e)
            task.save()
            raise