#!/usr/bin/env python3
"""
간단한 YouTube 크롤러 테스트
"""

import asyncio
from youtube_crawler import YouTubeCrawler, ConfigManager

async def test_simple():
    """간단한 테스트"""
    
    # 최적화된 설정
    config = ConfigManager()
    config.update({
        'max_workers': 2,      # 작업자 수 제한
        'timeout': 15,         # 짧은 타임아웃
        'cache_enabled': True,
        'headless': True,
        'scroll_count': 2,     # 스크롤 횟수 제한
        'wait_time': 1.0,      # 짧은 대기 시간
        'max_memory_mb': 1024  # 메모리 제한
    })
    
    print("=== 간단한 테스트 시작 ===")
    
    try:
        with YouTubeCrawler(config=config) as crawler:
            
            # 단일 키워드로 영상 검색
            print("1. 영상 검색 테스트...")
            videos = await crawler.search_videos_async(
                keywords=["파이썬 기초"],
                max_videos_per_keyword=3  # 적은 수로 테스트
            )
            
            print(f"검색 완료: {len(videos)}개 영상")
            
            if videos:
                # 첫 번째 영상의 댓글만 수집
                print("2. 댓글 수집 테스트...")
                first_video = videos[0]
                comments = await crawler.get_video_comments_async(
                    video_id=first_video['video_id'],
                    max_comments=5  # 적은 수로 테스트
                )
                
                print(f"댓글 수집 완료: {len(comments)}개 댓글")
                
                # 성능 메트릭 확인
                metrics = crawler.get_performance_metrics()
                print(f"\n=== 성능 메트릭 ===")
                print(f"메모리 사용량: {metrics['memory_usage_mb']:.2f} MB")
                print(f"캐시 활성화: {metrics['cache_enabled']}")
                
                # 엑셀 저장 테스트
                print("3. 엑셀 저장 테스트...")
                filename = await crawler.save_to_excel_async(
                    videos=videos,
                    comments=comments,
                    filename="test_output.xlsx"
                )
                
                if filename:
                    print(f"저장 완료: {filename}")
                
            print("\n=== 테스트 완료 ===")
            
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple()) 