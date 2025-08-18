#!/usr/bin/env python3
"""
유튜브 크롤러 성능 테스트 스크립트
실서버 환경에서 시스템 성능을 종합적으로 테스트합니다.
"""

import time
import psutil
import gc
import os
import sys
from datetime import datetime
import json
from typing import Dict, List, Any

# 프로젝트 모듈 import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from youtube_crawler import YouTubeCrawler

class PerformanceTester:
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.memory_usage = []
        self.cpu_usage = []
        
    def start_test(self, test_name: str):
        """테스트 시작"""
        self.start_time = time.time()
        self.memory_usage = []
        self.cpu_usage = []
        print(f"\n🚀 {test_name} 테스트 시작...")
        
    def end_test(self, test_name: str) -> Dict[str, Any]:
        """테스트 종료 및 결과 반환"""
        if not self.start_time:
            return {}
            
        total_time = time.time() - self.start_time
        avg_memory = sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0
        avg_cpu = sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0
        
        result = {
            'test_name': test_name,
            'total_time': total_time,
            'avg_memory_mb': avg_memory,
            'avg_cpu_percent': avg_cpu,
            'max_memory_mb': max(self.memory_usage) if self.memory_usage else 0,
            'max_cpu_percent': max(self.cpu_usage) if self.cpu_usage else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        self.test_results[test_name] = result
        print(f"✅ {test_name} 테스트 완료 - {total_time:.2f}초")
        return result
        
    def record_metrics(self):
        """시스템 메트릭 기록"""
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        cpu_percent = psutil.cpu_percent()
        
        self.memory_usage.append(memory_mb)
        self.cpu_usage.append(cpu_percent)
        
    def test_system_initialization(self):
        """시스템 초기화 테스트"""
        self.start_test("시스템 초기화")
        
        # 메모리 정리
        gc.collect()
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # YouTubeCrawler 초기화
        crawler = YouTubeCrawler()
        self.record_metrics()
        
        # 설정 업데이트
        config = {
            'max_workers': 4,
            'enable_keyword_analysis': True,
            'excel_encoding': 'utf-8-sig',
            'max_comments_per_video': 10
        }
        crawler.update_config(config)
        self.record_metrics()
        
        # 크롤러 종료
        crawler.close()
        self.record_metrics()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        result = self.end_test("시스템 초기화")
        result['memory_increase_mb'] = memory_increase
        return result
        
    def test_video_search(self, keywords: List[str], videos_per_keyword: int = 5):
        """영상 검색 성능 테스트"""
        test_name = f"영상 검색 ({len(keywords)}개 키워드, {videos_per_keyword}개씩)"
        self.start_test(test_name)
        
        crawler = YouTubeCrawler()
        config = {
            'max_workers': 4,
            'enable_keyword_analysis': False,
            'excel_encoding': 'utf-8-sig',
            'max_comments_per_video': 0
        }
        crawler.update_config(config)
        
        total_videos = 0
        search_times = []
        
        for keyword in keywords:
            keyword_start = time.time()
            self.record_metrics()
            
            videos = crawler.search_videos([keyword], videos_per_keyword)
            total_videos += len(videos)
            
            keyword_time = time.time() - keyword_start
            search_times.append(keyword_time)
            self.record_metrics()
            
            print(f"  - '{keyword}': {len(videos)}개 영상, {keyword_time:.2f}초")
            
        crawler.close()
        self.record_metrics()
        
        result = self.end_test(test_name)
        result['total_videos'] = total_videos
        result['avg_search_time'] = sum(search_times) / len(search_times)
        result['keywords'] = keywords
        return result
        
    def test_comment_collection(self, video_ids: List[str], comments_per_video: int = 5):
        """댓글 수집 성능 테스트"""
        test_name = f"댓글 수집 ({len(video_ids)}개 영상, {comments_per_video}개씩)"
        self.start_test(test_name)
        
        crawler = YouTubeCrawler()
        config = {
            'max_workers': 2,  # 댓글 수집은 더 적은 워커 사용
            'enable_keyword_analysis': False,
            'excel_encoding': 'utf-8-sig',
            'max_comments_per_video': comments_per_video
        }
        crawler.update_config(config)
        
        total_comments = 0
        comment_times = []
        
        for video_id in video_ids:
            comment_start = time.time()
            self.record_metrics()
            
            try:
                comments = crawler.get_video_comments(video_id, comments_per_video)
                total_comments += len(comments)
                comment_time = time.time() - comment_start
                comment_times.append(comment_time)
                
                print(f"  - 영상 {video_id}: {len(comments)}개 댓글, {comment_time:.2f}초")
                
            except Exception as e:
                print(f"  - 영상 {video_id}: 오류 발생 - {str(e)[:50]}...")
                comment_times.append(0)
                
            self.record_metrics()
            
        crawler.close()
        self.record_metrics()
        
        result = self.end_test(test_name)
        result['total_comments'] = total_comments
        result['avg_comment_time'] = sum(comment_times) / len(comment_times) if comment_times else 0
        result['successful_videos'] = len([t for t in comment_times if t > 0])
        return result
        
    def test_memory_management(self):
        """메모리 관리 테스트"""
        self.start_test("메모리 관리")
        
        # 대량 데이터 생성
        large_data = []
        for i in range(10000):
            large_data.append({
                'id': i,
                'title': f'Test Video {i}',
                'channel': f'Channel {i % 100}',
                'views': f'{i * 1000}',
                'data': 'x' * 1000  # 1KB 데이터
            })
            
        self.record_metrics()
        
        # 가비지 컬렉션
        del large_data
        gc.collect()
        self.record_metrics()
        
        result = self.end_test("메모리 관리")
        return result
        
    def test_concurrent_operations(self, num_operations: int = 5):
        """동시 작업 테스트"""
        test_name = f"동시 작업 ({num_operations}개)"
        self.start_test(test_name)
        
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def worker(worker_id):
            try:
                crawler = YouTubeCrawler()
                config = {
                    'max_workers': 1,
                    'enable_keyword_analysis': False,
                    'excel_encoding': 'utf-8-sig',
                    'max_comments_per_video': 0
                }
                crawler.update_config(config)
                
                # 간단한 검색 작업
                videos = crawler.search_videos(['test'], 1)
                crawler.close()
                
                results_queue.put({
                    'worker_id': worker_id,
                    'success': True,
                    'videos_count': len(videos)
                })
                
            except Exception as e:
                results_queue.put({
                    'worker_id': worker_id,
                    'success': False,
                    'error': str(e)
                })
        
        # 스레드 생성 및 시작
        threads = []
        for i in range(num_operations):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
            
        # 모든 스레드 완료 대기
        for thread in threads:
            thread.join()
            
        # 결과 수집
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
            
        self.record_metrics()
        
        result = self.end_test(test_name)
        result['successful_operations'] = len([r for r in results if r['success']])
        result['failed_operations'] = len([r for r in results if not r['success']])
        result['total_operations'] = len(results)
        return result
        
    def generate_report(self) -> str:
        """성능 테스트 리포트 생성"""
        report = []
        report.append("# 🚀 유튜브 크롤러 성능 테스트 리포트")
        report.append(f"**테스트 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**시스템 정보**: {os.uname().sysname} {os.uname().release}")
        report.append("")
        
        # 전체 통계
        total_tests = len(self.test_results)
        total_time = sum(r['total_time'] for r in self.test_results.values())
        avg_memory = sum(r['avg_memory_mb'] for r in self.test_results.values()) / total_tests if total_tests > 0 else 0
        max_memory = max(r['max_memory_mb'] for r in self.test_results.values()) if self.test_results else 0
        
        report.append("## 📊 전체 성능 요약")
        report.append(f"- **총 테스트 수**: {total_tests}개")
        report.append(f"- **총 실행 시간**: {total_time:.2f}초")
        report.append(f"- **평균 메모리 사용량**: {avg_memory:.1f} MB")
        report.append(f"- **최대 메모리 사용량**: {max_memory:.1f} MB")
        report.append("")
        
        # 개별 테스트 결과
        report.append("## 🔍 개별 테스트 결과")
        for test_name, result in self.test_results.items():
            report.append(f"### {result['test_name']}")
            report.append(f"- **실행 시간**: {result['total_time']:.2f}초")
            report.append(f"- **평균 메모리**: {result['avg_memory_mb']:.1f} MB")
            report.append(f"- **최대 메모리**: {result['max_memory_mb']:.1f} MB")
            report.append(f"- **평균 CPU**: {result['avg_cpu_percent']:.1f}%")
            report.append(f"- **최대 CPU**: {result['max_cpu_percent']:.1f}%")
            
            # 특별한 메트릭들
            if 'total_videos' in result:
                report.append(f"- **수집된 영상**: {result['total_videos']}개")
            if 'total_comments' in result:
                report.append(f"- **수집된 댓글**: {result['total_comments']}개")
            if 'successful_operations' in result:
                report.append(f"- **성공한 작업**: {result['successful_operations']}/{result['total_operations']}")
                
            report.append("")
            
        # 권장사항
        report.append("## 💡 성능 최적화 권장사항")
        
        if avg_memory > 500:
            report.append("- ⚠️ **메모리 사용량이 높습니다**. 동시 처리 수를 줄이거나 댓글 수집을 제한하세요.")
            
        if max_memory > 1000:
            report.append("- ⚠️ **최대 메모리 사용량이 높습니다**. 대용량 데이터 처리 시 주의하세요.")
            
        if total_time > 300:
            report.append("- ⚠️ **실행 시간이 길습니다**. 키워드 수나 영상 수를 줄여보세요.")
            
        report.append("- ✅ **캐시 기능을 활용**하여 중복 크롤링을 방지하세요.")
        report.append("- ✅ **메모리 정리 기능**을 주기적으로 사용하세요.")
        report.append("- ✅ **동시 처리 수**를 시스템 성능에 맞게 조정하세요.")
        
        return "\n".join(report)

def main():
    """메인 테스트 실행"""
    print("🚀 유튜브 크롤러 성능 테스트 시작")
    print("=" * 50)
    
    tester = PerformanceTester()
    
    try:
        # 1. 시스템 초기화 테스트
        tester.test_system_initialization()
        
        # 2. 영상 검색 테스트 (간단한 키워드)
        simple_keywords = ['python', 'programming']
        tester.test_video_search(simple_keywords, videos_per_keyword=3)
        
        # 3. 영상 검색 테스트 (복잡한 키워드)
        complex_keywords = ['machine learning', 'data science', 'artificial intelligence']
        result = tester.test_video_search(complex_keywords, videos_per_keyword=2)
        
        # 4. 댓글 수집 테스트 (수집된 영상 ID 사용)
        if 'total_videos' in result and result['total_videos'] > 0:
            # 실제 영상 ID 대신 테스트용 ID 사용
            test_video_ids = ['dQw4w9WgXcQ', 'jNQXAC9IVRw']  # 유명한 유튜브 영상 ID
            tester.test_comment_collection(test_video_ids, comments_per_video=3)
        
        # 5. 메모리 관리 테스트
        tester.test_memory_management()
        
        # 6. 동시 작업 테스트
        tester.test_concurrent_operations(3)
        
        # 7. 리포트 생성
        report = tester.generate_report()
        
        # 리포트 저장
        with open('performance_test_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
            
        # JSON 결과 저장
        with open('performance_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(tester.test_results, f, ensure_ascii=False, indent=2)
            
        print("\n" + "=" * 50)
        print("✅ 성능 테스트 완료!")
        print("📄 리포트: performance_test_report.md")
        print("📊 결과: performance_test_results.json")
        print("\n" + report)
        
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
