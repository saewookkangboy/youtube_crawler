#!/usr/bin/env python3
"""
성능 개선된 YouTube 크롤러 테스트 스크립트
- 크롤링 안정성 테스트
- 댓글 추출 속도 테스트
- 키워드 분석 테스트
- 발행일 파싱 테스트
- 엑셀 저장 테스트
"""

import asyncio
import time
from datetime import datetime, timedelta
from youtube_crawler import YouTubeCrawler, ConfigManager, PerformanceMonitor, KeywordAnalyzer

def test_crawler_stability():
    """크롤러 안정성 테스트"""
    print("🔧 크롤러 안정성 테스트 시작...")
    
    config = ConfigManager()
    config.update({
        'max_workers': 4,
        'timeout': 30,
        'retry_count': 3,
        'headless': True,
        'scroll_count': 2,
        'wait_time': 1.0
    })
    
    crawler = YouTubeCrawler(config)
    
    try:
        # 간단한 검색 테스트
        keywords = ["파이썬 튜토리얼"]
        videos = crawler.search_videos(keywords, max_videos_per_keyword=3)
        
        print(f"✅ 검색 성공: {len(videos)}개 영상 발견")
        
        if videos:
            # 첫 번째 영상의 댓글 테스트
            video_id = videos[0].get('video_id')
            if video_id:
                comments = crawler.get_video_comments(video_id, max_comments=5)
                print(f"✅ 댓글 수집 성공: {len(comments)}개 댓글")
        
        # 성능 메트릭 출력
        metrics = crawler.get_performance_metrics()
        print(f"📊 성능 메트릭: {metrics}")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
    finally:
        crawler.close()

def test_comment_extraction_speed():
    """댓글 추출 속도 테스트"""
    print("\n⚡ 댓글 추출 속도 테스트 시작...")
    
    config = ConfigManager()
    config.update({
        'max_workers': 6,
        'comment_batch_size': 10,
        'max_comments_per_video': 20
    })
    
    crawler = YouTubeCrawler(config)
    
    try:
        # 인기 영상 검색
        keywords = ["코딩"]
        videos = crawler.search_videos(keywords, max_videos_per_keyword=2)
        
        if videos:
            start_time = time.time()
            
            # 댓글 수집
            all_comments = []
            for video in videos:
                video_id = video.get('video_id')
                if video_id:
                    comments = crawler.get_video_comments(video_id, max_comments=10)
                    all_comments.extend(comments)
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            print(f"✅ 댓글 수집 완료: {len(all_comments)}개 댓글")
            print(f"⏱️ 소요 시간: {elapsed:.2f}초")
            print(f"🚀 평균 속도: {len(all_comments)/elapsed:.1f} 댓글/초")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
    finally:
        crawler.close()

def test_keyword_analysis():
    """키워드 분석 테스트"""
    print("\n🔍 키워드 분석 테스트 시작...")
    
    try:
        analyzer = KeywordAnalyzer()
        
        # 테스트 텍스트
        test_texts = [
            "파이썬 프로그래밍 언어는 정말 좋습니다",
            "코딩을 배우는 것이 재미있어요",
            "프로그래밍 기초를 공부하고 있습니다",
            "파이썬으로 웹 개발을 하고 있어요",
            "코딩 실력을 향상시키고 싶습니다"
        ]
        
        # 키워드 분석 실행
        start_time = time.time()
        analysis = analyzer.analyze_keywords(test_texts, top_n=10)
        end_time = time.time()
        
        print(f"✅ 키워드 분석 완료: {end_time - start_time:.3f}초")
        print(f"📊 분석 결과:")
        print(f"  - 상위 키워드: {analysis.get('top_keywords', {})}")
        print(f"  - 총 단어 수: {analysis.get('total_words', 0)}")
        print(f"  - 고유 단어 수: {analysis.get('unique_words', 0)}")
        print(f"  - 감정 점수: {analysis.get('sentiment_score', 0):.3f}")
        print(f"  - 감정 라벨: {analysis.get('sentiment_label', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 키워드 분석 테스트 실패: {e}")

def test_upload_time_parsing():
    """발행일 파싱 테스트"""
    print("\n📅 발행일 파싱 테스트 시작...")
    
    crawler = YouTubeCrawler()
    
    # 다양한 시간 형식 테스트
    test_times = [
        "3일 전",
        "1주 전", 
        "2개월 전",
        "1년 전",
        "2024. 1. 15.",
        "2024년 1월 15일",
        "2024-01-15",
        "방금 전",
        "5시간 전",
        "30분 전"
    ]
    
    for time_text in test_times:
        try:
            parsed_time = crawler._parse_upload_time(time_text)
            if parsed_time:
                formatted = parsed_time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"✅ '{time_text}' → {formatted}")
            else:
                print(f"⚠️ '{time_text}' → 파싱 실패")
        except Exception as e:
            print(f"❌ '{time_text}' → 오류: {e}")
    
    crawler.close()

def test_excel_saving():
    """엑셀 저장 테스트"""
    print("\n💾 엑셀 저장 테스트 시작...")
    
    config = ConfigManager()
    config.update({
        'excel_encoding': 'utf-8-sig',
        'enable_keyword_analysis': True
    })
    
    crawler = YouTubeCrawler(config)
    
    try:
        # 테스트 데이터 생성
        test_videos = [
            {
                'keyword': '테스트',
                'title': '테스트 영상 1',
                'channel_name': '테스트 채널',
                'view_count': '1,000회',
                'upload_time': '3일 전',
                'video_id': 'test123',
                'video_url': 'https://youtube.com/watch?v=test123'
            },
            {
                'keyword': '테스트',
                'title': '테스트 영상 2', 
                'channel_name': '테스트 채널',
                'view_count': '2,000회',
                'upload_time': '1주 전',
                'video_id': 'test456',
                'video_url': 'https://youtube.com/watch?v=test456'
            }
        ]
        
        test_comments = [
            {
                'video_id': 'test123',
                'comment_text': '정말 좋은 영상이네요!',
                'author': '사용자1',
                'like_count': 10,
                'comment_time': '2일 전'
            },
            {
                'video_id': 'test123',
                'comment_text': '도움이 많이 되었습니다',
                'author': '사용자2', 
                'like_count': 5,
                'comment_time': '1일 전'
            }
        ]
        
        # 엑셀 저장 테스트
        filename = "test_output.xlsx"
        start_time = time.time()
        
        saved_file = crawler.save_to_excel(test_videos, test_comments, filename)
        
        end_time = time.time()
        
        if saved_file:
            print(f"✅ 엑셀 저장 성공: {saved_file}")
            print(f"⏱️ 저장 시간: {end_time - start_time:.3f}초")
        else:
            print("❌ 엑셀 저장 실패")
            
    except Exception as e:
        print(f"❌ 엑셀 저장 테스트 실패: {e}")
    finally:
        crawler.close()

async def test_async_performance():
    """비동기 성능 테스트"""
    print("\n🚀 비동기 성능 테스트 시작...")
    
    config = ConfigManager()
    config.update({
        'max_workers': 6,
        'max_comments_per_video': 10
    })
    
    crawler = YouTubeCrawler(config)
    
    try:
        # 비동기 검색 테스트
        keywords = ["파이썬", "코딩"]
        start_time = time.time()
        
        videos = await crawler.search_videos_async(keywords, max_videos_per_keyword=2)
        
        if videos:
            # 비동기 댓글 수집 테스트
            comments = await crawler.get_comments_for_videos_async(videos, max_comments_per_video=5)
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            print(f"✅ 비동기 처리 완료:")
            print(f"  - 영상 수: {len(videos)}")
            print(f"  - 댓글 수: {len(comments)}")
            print(f"  - 소요 시간: {elapsed:.2f}초")
            
    except Exception as e:
        print(f"❌ 비동기 테스트 실패: {e}")
    finally:
        crawler.close()

def main():
    """메인 테스트 함수"""
    print("🎯 YouTube 크롤러 성능 개선 테스트 시작")
    print("=" * 50)
    
    # 1. 크롤러 안정성 테스트
    test_crawler_stability()
    
    # 2. 댓글 추출 속도 테스트
    test_comment_extraction_speed()
    
    # 3. 키워드 분석 테스트
    test_keyword_analysis()
    
    # 4. 발행일 파싱 테스트
    test_upload_time_parsing()
    
    # 5. 엑셀 저장 테스트
    test_excel_saving()
    
    # 6. 비동기 성능 테스트
    asyncio.run(test_async_performance())
    
    print("\n" + "=" * 50)
    print("🎉 모든 테스트 완료!")

if __name__ == "__main__":
    main()
