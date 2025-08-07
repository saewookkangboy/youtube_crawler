#!/usr/bin/env python3
"""
최적화된 YouTube 크롤러 사용 예제
"""

import asyncio
from datetime import datetime, timedelta
from youtube_crawler import YouTubeCrawler, ConfigManager

async def main():
    """메인 함수 - 비동기 실행"""
    
    # 설정 관리자 생성
    config = ConfigManager()
    
    # 성능 최적화 설정
    config.update({
        'max_workers': 6,  # 동시 작업 수 증가
        'timeout': 20,     # 타임아웃 단축
        'cache_enabled': True,
        'headless': True,
        'scroll_count': 3,  # 스크롤 횟수 최적화
        'wait_time': 1.5,   # 대기 시간 최적화
        'max_memory_mb': 3072  # 메모리 제한 증가
    })
    
    # 컨텍스트 매니저로 크롤러 사용
    with YouTubeCrawler(config=config) as crawler:
        
        # 검색 키워드
        keywords = ["파이썬 튜토리얼", "머신러닝 기초", "데이터 분석"]
        
        # 날짜 범위 설정 (최근 1개월)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        print("=== 비동기 영상 검색 시작 ===")
        
        # 비동기 영상 검색
        videos = await crawler.search_videos_async(
            keywords=keywords,
            max_videos_per_keyword=15,
            start_date=start_date,
            end_date=end_date
        )
        
        print(f"검색 완료: {len(videos)}개 영상 발견")
        
        if videos:
            print("\n=== 비동기 댓글 수집 시작 ===")
            
            # 비동기 댓글 수집 (상위 10개 영상만)
            top_videos = videos[:10]
            comments = await crawler.get_comments_for_videos_async(
                videos=top_videos,
                max_comments_per_video=30
            )
            
            print(f"댓글 수집 완료: {len(comments)}개 댓글")
            
            # 성능 메트릭 확인
            metrics = crawler.get_performance_metrics()
            print(f"\n=== 성능 메트릭 ===")
            print(f"메모리 사용량: {metrics['memory_usage_mb']:.2f} MB")
            print(f"캐시 활성화: {metrics['cache_enabled']}")
            print(f"작업자 수: {metrics['max_workers']}")
            
            # 엑셀 저장
            print("\n=== 데이터 저장 ===")
            filename = await crawler.save_to_excel_async(
                videos=videos,
                comments=comments,
                filename=f"youtube_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if filename:
                print(f"데이터가 {filename}에 저장되었습니다.")
        
        print("\n=== 작업 완료 ===")

def sync_example():
    """동기 실행 예제 (기존 호환성)"""
    
    # 기본 설정으로 크롤러 생성
    with YouTubeCrawler() as crawler:
        
        keywords = ["파이썬 기초"]
        
        # 동기 영상 검색
        videos = crawler.search_videos(
            keywords=keywords,
            max_videos_per_keyword=5
        )
        
        print(f"동기 검색 완료: {len(videos)}개 영상")
        
        if videos:
            # 동기 댓글 수집
            comments = crawler.get_comments_for_videos(
                videos=videos[:3],
                max_comments_per_video=20
            )
            
            print(f"동기 댓글 수집 완료: {len(comments)}개 댓글")
            
            # 엑셀 저장
            filename = crawler.save_to_excel(videos, comments)
            if filename:
                print(f"동기 저장 완료: {filename}")

async def advanced_example():
    """고급 사용 예제"""
    
    # 고성능 설정
    config = ConfigManager()
    config.update({
        'max_workers': 8,
        'timeout': 15,
        'cache_enabled': True,
        'headless': True,
        'scroll_count': 2,
        'wait_time': 1.0,
        'max_memory_mb': 4096
    })
    
    with YouTubeCrawler(config=config) as crawler:
        
        # 대량 키워드 검색
        keywords = [
            "파이썬 프로그래밍", "자바스크립트", "리액트", "뷰.js",
            "데이터 사이언스", "인공지능", "딥러닝", "머신러닝"
        ]
        
        print("=== 대량 검색 시작 ===")
        
        # 비동기 검색
        videos = await crawler.search_videos_async(
            keywords=keywords,
            max_videos_per_keyword=20
        )
        
        print(f"대량 검색 완료: {len(videos)}개 영상")
        
        if videos:
            # 배치 댓글 수집
            print("=== 배치 댓글 수집 시작 ===")
            
            # 영상을 배치로 나누어 처리
            batch_size = 5
            all_comments = []
            
            for i in range(0, len(videos), batch_size):
                batch = videos[i:i+batch_size]
                print(f"배치 {i//batch_size + 1} 처리 중... ({len(batch)}개 영상)")
                
                batch_comments = await crawler.get_comments_for_videos_async(
                    videos=batch,
                    max_comments_per_video=25
                )
                
                all_comments.extend(batch_comments)
                
                # 메모리 최적화
                crawler.optimize_memory()
            
            print(f"배치 댓글 수집 완료: {len(all_comments)}개 댓글")
            
            # 성능 메트릭 출력
            metrics = crawler.get_performance_metrics()
            print(f"\n=== 최종 성능 메트릭 ===")
            for key, value in metrics['metrics'].items():
                if 'duration' in value:
                    print(f"{key}: {value['duration']:.2f}초")
            
            # 결과 저장
            filename = await crawler.save_to_excel_async(
                videos=videos,
                comments=all_comments,
                filename=f"advanced_youtube_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if filename:
                print(f"고급 예제 완료: {filename}")

if __name__ == "__main__":
    print("=== 최적화된 YouTube 크롤러 예제 ===")
    
    # 실행 모드 선택
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        mode = "async"
    
    if mode == "async":
        print("비동기 모드로 실행...")
        asyncio.run(main())
    elif mode == "sync":
        print("동기 모드로 실행...")
        sync_example()
    elif mode == "advanced":
        print("고급 모드로 실행...")
        asyncio.run(advanced_example())
    else:
        print("사용법: python example_optimized.py [async|sync|advanced]")
        print("기본값: async")
        asyncio.run(main()) 