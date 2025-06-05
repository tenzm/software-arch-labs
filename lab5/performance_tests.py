#!/usr/bin/env python3
"""
Скрипт для тестирования производительности User Service с и без кеша.
Использует wrk для нагрузочного тестирования и генерирует CSV отчеты.
"""

import subprocess
import json
import csv
import time
import os
import sys
import random
from datetime import datetime


class PerformanceTestRunner:
    def __init__(self):
        self.base_url = "http://localhost:8080/api/v1"
        self.results = []
        
    def run_wrk_test(self, url: str, threads: int, duration: int = 30) -> dict:
        """Запустить wrk тест и парсить результаты"""
        print(f"Running wrk test with {threads} threads on {url}")
        
        cmd = [
            "wrk",
            "-t", str(threads),
            "-c", str(threads * 10),  # connections = threads * 10
            "-d", f"{duration}s",
            "--latency",
            url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 10)
            
            if result.returncode != 0:
                print(f"wrk failed: {result.stderr}")
                return None
                
            return self.parse_wrk_output(result.stdout, threads, url)
            
        except subprocess.TimeoutExpired:
            print(f"wrk test timed out for {url}")
            return None
        except FileNotFoundError:
            print("wrk not found. Please install wrk: https://github.com/wg/wrk")
            return None
    
    def parse_wrk_output(self, output: str, threads: int, url: str) -> dict:
        """Парсить вывод wrk"""
        lines = output.strip().split('\n')
        
        result = {
            "url": url,
            "threads": threads,
            "timestamp": datetime.now().isoformat()
        }
        
        for line in lines:
            line = line.strip()
            
            # Парсим основные метрики
            if "Requests/sec:" in line:
                result["requests_per_sec"] = float(line.split(":")[1].strip())
            elif "Transfer/sec:" in line:
                result["transfer_per_sec"] = line.split(":")[1].strip()
            elif "requests in" in line and "read" in line:
                # Парсим общую информацию
                parts = line.split(",")
                for part in parts:
                    part = part.strip()
                    if "requests in" in part:
                        result["total_requests"] = int(part.split()[0])
                        # Извлекаем время
                        time_part = part.split("in")[1].strip()
                        result["test_duration"] = time_part
                    elif "read" in part:
                        result["data_read"] = part.strip()
            elif "Socket errors:" in line:
                # Парсим ошибки если есть
                error_parts = line.split(":")[1].strip().split(",")
                result["socket_errors"] = line.split(":")[1].strip()
            elif "Latency" in line and not "Distribution" in line:
                # Парсим латентность
                latency_parts = line.split()
                if len(latency_parts) >= 4:
                    result["latency_avg"] = latency_parts[1]
                    result["latency_stdev"] = latency_parts[2]
                    result["latency_max"] = latency_parts[3]
            elif "99%" in line:
                # Парсим процентили латентности
                percentile_parts = line.split()
                if len(percentile_parts) >= 2:
                    result["latency_99th"] = percentile_parts[1]
        
        return result
    
    def get_random_user_ids(self, count: int = 50) -> list:
        """Получить случайные ID пользователей для тестирования"""
        # Предполагаем, что у нас есть пользователи от testuser0 до testuser999
        # Возвращаем случайные UUID-like строки для имитации
        import uuid
        return [str(uuid.uuid4()) for _ in range(count)]
    
    def run_cache_vs_no_cache_tests(self):
        """Запустить сравнительные тесты кеша vs без кеша"""
        thread_counts = [1, 5, 10]
        
        print("Starting cache vs no-cache performance tests...")
        print(f"Thread counts: {thread_counts}")
        
        for threads in thread_counts:
            print(f"\n=== Testing with {threads} threads ===")
            
            # Тест 1: Получение списка пользователей с кешем
            print("Testing users list WITH cache...")
            cache_result = self.run_wrk_test(
                f"{self.base_url}/performance/users?limit=50&offset=0",
                threads
            )
            if cache_result:
                cache_result["test_type"] = "users_list_with_cache"
                cache_result["cache_enabled"] = True
                self.results.append(cache_result)
            
            # Небольшая пауза между тестами
            time.sleep(2)
            
            # Тест 2: Получение списка пользователей без кеша
            print("Testing users list WITHOUT cache...")
            no_cache_result = self.run_wrk_test(
                f"{self.base_url}/performance/users-no-cache?limit=50&offset=0",
                threads
            )
            if no_cache_result:
                no_cache_result["test_type"] = "users_list_no_cache"
                no_cache_result["cache_enabled"] = False
                self.results.append(no_cache_result)
            
            # Пауза между разными количествами потоков
            time.sleep(5)
    
    def generate_csv_report(self, filename: str = None):
        """Генерировать CSV отчет с результатами"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_test_results_{timestamp}.csv"
        
        if not self.results:
            print("No test results to save")
            return
        
        print(f"Generating CSV report: {filename}")
        
        # Определяем все возможные поля
        all_fields = set()
        for result in self.results:
            all_fields.update(result.keys())
        
        fieldnames = sorted(list(all_fields))
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.results:
                writer.writerow(result)
        
        print(f"Results saved to {filename}")
        
        # Также выводим краткую сводку
        self.print_summary()
    
    def print_summary(self):
        """Вывести краткую сводку результатов"""
        print("\n" + "="*60)
        print("PERFORMANCE TEST SUMMARY")
        print("="*60)
        
        for threads in [1, 5, 10]:
            print(f"\n--- {threads} thread(s) ---")
            
            cache_results = [r for r in self.results 
                           if r.get("threads") == threads and r.get("cache_enabled") == True]
            no_cache_results = [r for r in self.results 
                              if r.get("threads") == threads and r.get("cache_enabled") == False]
            
            if cache_results and no_cache_results:
                cache_rps = cache_results[0].get("requests_per_sec", 0)
                no_cache_rps = no_cache_results[0].get("requests_per_sec", 0)
                
                if no_cache_rps > 0:
                    improvement = ((cache_rps - no_cache_rps) / no_cache_rps) * 100
                    print(f"With Cache:    {cache_rps:.2f} req/sec")
                    print(f"Without Cache: {no_cache_rps:.2f} req/sec")
                    print(f"Improvement:   {improvement:+.1f}%")
                else:
                    print("No valid results for comparison")
    
    def run_all_tests(self):
        """Запустить все тесты"""
        print("Starting User Service Performance Tests")
        print("="*50)
        
        # Проверяем, что сервис доступен
        try:
            import requests
            response = requests.get(f"{self.base_url.replace('/api/v1', '')}/health", timeout=5)
            if response.status_code != 200:
                print(f"Service health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"Cannot reach service at {self.base_url}: {e}")
            print("Make sure the service is running: docker-compose up")
            return False
        
        # Запускаем тесты
        self.run_cache_vs_no_cache_tests()
        
        # Генерируем отчет
        self.generate_csv_report()
        
        return True


def main():
    """Главная функция"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python performance_tests.py")
        print("Make sure the User Service is running on http://localhost:8080")
        print("Also ensure wrk is installed: https://github.com/wg/wrk")
        return
    
    runner = PerformanceTestRunner()
    
    print("Cache Performance Test Suite")
    print("===========================")
    print("This script will test User Service performance with and without Redis cache")
    print("using wrk load testing tool with 1, 5, and 10 threads.")
    print("")
    print("Prerequisites:")
    print("1. User Service should be running (docker-compose up)")
    print("2. Database should be populated with test data")
    print("3. wrk should be installed")
    print("")
    
    input("Press Enter to continue...")
    
    success = runner.run_all_tests()
    
    if success:
        print("\nPerformance tests completed successfully!")
        print("Check the generated CSV file for detailed results.")
    else:
        print("\nPerformance tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 