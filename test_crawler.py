#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
유튜브 크롤러 테스트 스크립트
기본적인 기능을 테스트하고 샘플 데이터를 생성합니다.
"""

import sys
import os
import time
from datetime import datetime, timedelta
from youtube_crawler import YouTubeCrawler

def test_basic_functionality():
    """기본 기능 테스트"""
    print("🧪 유튜브 크롤러 기본 기능 테스트")
    print("=" * 50)
    
    # 테스트 키워드
    test_keywords = ["파이썬 튜토리얼", "머신러닝 기초", "데이터 분석"]
    
    crawler = None
    try:
        print("1️⃣ 크롤러 초기화 테스트...")
        crawler = YouTubeCrawler()
        print("✅ 크롤러 초기화 성공")
        
        print("\n2️⃣ 영상 검색 테스트...")
        print(f"   검색 키워드: {', '.join(test_keywords)}")
        print("   각 키워드당 3개 영상만 수집 (테스트용)")
        
        # 날짜 필터링 테스트 (최근 30일)
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        print(f"   날짜 범위: {start_date.strftime('%Y년 %m월 %d일')} ~ {end_date.strftime('%Y년 %m월 %d일')}")
        
        videos = crawler.search_videos(test_keywords, max_videos_per_keyword=3, start_date=start_date, end_date=end_date)
        
        if videos:
            print(f"✅ {len(videos)}개의 영상을 성공적으로 수집했습니다.")
            
            # 수집된 영상 정보 출력
            print("\n📋 수집된 영상 정보:")
            for i, video in enumerate(videos, 1):
                print(f"   {i}. {video['title'][:60]}...")
                print(f"      채널: {video['channel_name']}")
                print(f"      조회수: {video['view_count']}")
                print(f"      URL: {video['video_url']}")
                print()
            
            # 댓글 수집 테스트 (첫 번째 영상만)
            if videos and videos[0].get('video_id'):
                print("3️⃣ 댓글 수집 테스트...")
                print(f"   테스트 영상: {videos[0]['title'][:50]}...")
                
                comments = crawler.get_video_comments(videos[0]['video_id'], max_comments=5)
                
                if comments:
                    print(f"✅ {len(comments)}개의 댓글을 성공적으로 수집했습니다.")
                    print("\n📝 수집된 댓글:")
                    for i, comment in enumerate(comments, 1):
                        print(f"   {i}. {comment['comment'][:100]}...")
                else:
                    print("⚠️  댓글을 수집할 수 없었습니다.")
            
            # 엑셀 저장 테스트
            print("\n4️⃣ 엑셀 저장 테스트...")
            test_filename = "test_youtube_data.xlsx"
            saved_file = crawler.save_to_excel(videos, comments if 'comments' in locals() else [], test_filename)
            
            if saved_file:
                print(f"✅ 테스트 데이터가 {saved_file}에 저장되었습니다.")
                print(f"   파일 위치: {os.path.abspath(saved_file)}")
            else:
                print("❌ 엑셀 저장에 실패했습니다.")
        
        else:
            print("❌ 영상을 수집할 수 없었습니다.")
            
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if crawler:
            crawler.close()
            print("\n🔒 브라우저가 종료되었습니다.")

def test_single_keyword():
    """단일 키워드 테스트"""
    print("\n🧪 단일 키워드 테스트")
    print("=" * 30)
    
    keyword = input("테스트할 키워드를 입력하세요: ").strip()
    if not keyword:
        keyword = "파이썬"
    
    crawler = None
    try:
        crawler = YouTubeCrawler()
        print(f"🔍 '{keyword}' 키워드로 5개 영상 검색 중...")
        
        videos = crawler.search_videos([keyword], max_videos_per_keyword=5)
        
        if videos:
            print(f"✅ {len(videos)}개의 영상을 찾았습니다.")
            
            # 간단한 통계
            channels = {}
            for video in videos:
                channel = video['channel_name']
                channels[channel] = channels.get(channel, 0) + 1
            
            print(f"\n📊 통계:")
            print(f"   - 총 영상 수: {len(videos)}")
            print(f"   - 참여 채널 수: {len(channels)}")
            print(f"   - 가장 많은 영상: {max(channels.items(), key=lambda x: x[1])[0]} ({max(channels.values())}개)")
            
        else:
            print("❌ 영상을 찾을 수 없었습니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        if crawler:
            crawler.close()

def main():
    """메인 테스트 함수"""
    print("🎥 유튜브 크롤러 테스트 스크립트")
    print("=" * 50)
    
    while True:
        print("\n테스트 옵션을 선택하세요:")
        print("1. 기본 기능 테스트 (자동)")
        print("2. 단일 키워드 테스트 (수동)")
        print("3. 종료")
        
        choice = input("\n선택 (1-3): ").strip()
        
        if choice == "1":
            test_basic_functionality()
        elif choice == "2":
            test_single_keyword()
        elif choice == "3":
            print("👋 테스트를 종료합니다.")
            break
        else:
            print("❌ 잘못된 선택입니다. 1-3 중에서 선택해주세요.")

if __name__ == "__main__":
    main() 