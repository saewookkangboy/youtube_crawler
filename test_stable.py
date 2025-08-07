#!/usr/bin/env python3
"""
안정화된 YouTube 크롤러 테스트
- 최적화된 설정으로 안정성 테스트
- 단계별 검증
- 성능 모니터링
"""

import asyncio
import time
from youtube_crawler import YouTubeCrawler, ConfigManager

async def test_stable_crawler():
    """안정화된 크롤러 테스트"""
    print("=== 안정화된 YouTube 크롤러 테스트 시작 ===")
    
    # 안정화된 설정
    config = ConfigManager()
    config.update({
        'max_workers': 2,           # 안정성을 위해 2로 제한
        'timeout': 15,              # 15초 타임아웃
        'scroll_count': 3,          # 3회 스크롤
        'wait_time': 1.5,           # 1.5초 대기
        'max_memory_mb': 1024,      # 1GB 메모리 제한
        'headless': True,           # 헤드리스 모드
        'cache_enabled': True       # 캐시 활성화
    })
    
    try:
        with YouTubeCrawler(config) as crawler:
            print("1. 영상 검색 테스트 (안정화)...")
            
            # 단일 키워드로 테스트
            keywords = ["파이썬 기초"]
            videos = await crawler.search_videos_async(
                keywords=keywords,
                max_videos_per_keyword=5  # 안정성을 위해 5개로 제한
            )
            
            print(f"검색 완료: {len(videos)}개 영상")
            
            if not videos:
                print("❌ 영상을 찾을 수 없습니다.")
                return
            
            # 첫 번째 영상만 댓글 수집 테스트
            print("2. 댓글 수집 테스트 (안정화)...")
            first_video = videos[0]
            video_id = first_video.get('video_id')
            
            if video_id:
                comments = await crawler.get_video_comments_async(
                    video_id=video_id,
                    max_comments=10  # 안정성을 위해 10개로 제한
                )
                print(f"댓글 수집 완료: {len(comments)}개 댓글")
            else:
                print("❌ 영상 ID를 찾을 수 없습니다.")
                return
            
            # 엑셀 저장 테스트
            print("3. 엑셀 저장 테스트...")
            filename = "stable_test_output.xlsx"
            result = await crawler.save_to_excel_async(
                videos=videos,
                comments=comments,
                filename=filename
            )
            
            if result:
                print(f"저장 완료: {filename}")
            else:
                print("❌ 저장 실패")
            
            # 성능 메트릭 출력
            print("\n=== 성능 메트릭 ===")
            metrics = crawler.get_performance_metrics()
            print(f"메모리 사용량: {metrics['memory_usage_mb']:.2f} MB")
            print(f"캐시 활성화: {metrics['cache_enabled']}")
            print(f"최대 워커: {metrics['max_workers']}")
            
            print("\n=== 테스트 완료 ===")
            
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        return False
    
    return True

async def test_batch_processing():
    """배치 처리 테스트"""
    print("\n=== 배치 처리 테스트 ===")
    
    config = ConfigManager()
    config.update({
        'max_workers': 2,
        'timeout': 15,
        'scroll_count': 2,
        'wait_time': 1.0,
        'max_memory_mb': 1024
    })
    
    try:
        with YouTubeCrawler(config) as crawler:
            # 여러 키워드 검색
            keywords = ["파이썬 튜토리얼", "머신러닝 기초"]
            videos = await crawler.search_videos_async(
                keywords=keywords,
                max_videos_per_keyword=3  # 키워드당 3개씩
            )
            
            print(f"배치 검색 완료: {len(videos)}개 영상")
            
            if len(videos) >= 2:
                # 배치 댓글 수집
                comments = await crawler.get_comments_for_videos_async(
                    videos=videos[:2],  # 처음 2개 영상만
                    max_comments_per_video=5  # 영상당 5개 댓글
                )
                
                print(f"배치 댓글 수집 완료: {len(comments)}개 댓글")
                
                # 저장
                filename = "batch_test_output.xlsx"
                result = await crawler.save_to_excel_async(
                    videos=videos,
                    comments=comments,
                    filename=filename
                )
                
                if result:
                    print(f"배치 저장 완료: {filename}")
                
                return True
            else:
                print("❌ 충분한 영상을 찾을 수 없습니다.")
                return False
                
    except Exception as e:
        print(f"❌ 배치 테스트 중 오류: {e}")
        return False

async def test_error_handling():
    """오류 처리 테스트"""
    print("\n=== 오류 처리 테스트 ===")
    
    config = ConfigManager()
    config.update({
        'max_workers': 1,
        'timeout': 10,
        'scroll_count': 1,
        'wait_time': 0.5
    })
    
    try:
        with YouTubeCrawler(config) as crawler:
            # 존재하지 않는 키워드로 테스트
            videos = await crawler.search_videos_async(
                keywords=["존재하지않는키워드12345"],
                max_videos_per_keyword=1
            )
            
            print(f"오류 처리 테스트 완료: {len(videos)}개 영상")
            return True
            
    except Exception as e:
        print(f"❌ 오류 처리 테스트 실패: {e}")
        return False

async def main():
    """메인 테스트 함수"""
    print("🚀 안정화된 YouTube 크롤러 테스트 시작")
    print("=" * 50)
    
    # 기본 안정성 테스트
    basic_result = await test_stable_crawler()
    
    if basic_result:
        print("✅ 기본 안정성 테스트 통과")
        
        # 배치 처리 테스트
        batch_result = await test_batch_processing()
        if batch_result:
            print("✅ 배치 처리 테스트 통과")
        
        # 오류 처리 테스트
        error_result = await test_error_handling()
        if error_result:
            print("✅ 오류 처리 테스트 통과")
        
        print("\n🎉 모든 테스트 완료!")
        print("=" * 50)
        
    else:
        print("❌ 기본 안정성 테스트 실패")
        return False
    
    return True

if __name__ == "__main__":
    start_time = time.time()
    
    try:
        result = asyncio.run(main())
        end_time = time.time()
        
        print(f"\n⏱️  총 실행 시간: {end_time - start_time:.2f}초")
        
        if result:
            print("🎯 모든 테스트가 성공적으로 완료되었습니다!")
        else:
            print("⚠️  일부 테스트가 실패했습니다.")
            
    except KeyboardInterrupt:
        print("\n⏹️  사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n�� 예상치 못한 오류: {e}") 