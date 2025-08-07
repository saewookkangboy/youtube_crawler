#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime
from youtube_crawler import YouTubeCrawler

def main():
    print("=" * 60)
    print("🎥 유튜브 크롤러 및 데이터 정리 서비스")
    print("=" * 60)
    
    # 키워드 입력 받기
    print("\n📝 검색할 키워드를 입력하세요 (3~5개, 쉼표로 구분):")
    keywords_input = input("키워드: ").strip()
    
    if not keywords_input:
        print("❌ 키워드를 입력해주세요.")
        return
    
    # 키워드 파싱
    keywords = [keyword.strip() for keyword in keywords_input.split(',')]
    keywords = [k for k in keywords if k]  # 빈 문자열 제거
    
    if len(keywords) < 3 or len(keywords) > 5:
        print("❌ 키워드는 3~5개를 입력해주세요.")
        return
    
    print(f"\n✅ 입력된 키워드: {', '.join(keywords)}")
    
    # 영상 수 설정
    print("\n📊 키워드당 수집할 영상 수를 입력하세요 (기본값: 10):")
    videos_per_keyword_input = input("영상 수: ").strip()
    
    try:
        videos_per_keyword = int(videos_per_keyword_input) if videos_per_keyword_input else 10
    except ValueError:
        videos_per_keyword = 10
        print("⚠️  잘못된 입력으로 기본값 10을 사용합니다.")
    
    # 댓글 수집 여부
    print("\n💬 댓글도 수집하시겠습니까? (y/n, 기본값: n):")
    collect_comments_input = input("댓글 수집: ").strip().lower()
    collect_comments = collect_comments_input in ['y', 'yes', '예', '네']
    
    if collect_comments:
        print("\n📝 영상당 수집할 댓글 수를 입력하세요 (기본값: 20):")
        comments_per_video_input = input("댓글 수: ").strip()
        try:
            comments_per_video = int(comments_per_video_input) if comments_per_video_input else 20
        except ValueError:
            comments_per_video = 20
            print("⚠️  잘못된 입력으로 기본값 20을 사용합니다.")
    else:
        comments_per_video = 0
    
    # 날짜 범위 설정
    print("\n📅 수집 기간을 설정하시겠습니까? (y/n, 기본값: n):")
    use_date_filter_input = input("날짜 필터 사용: ").strip().lower()
    use_date_filter = use_date_filter_input in ['y', 'yes', '예', '네']
    
    start_date = None
    end_date = None
    
    if use_date_filter:
        print("\n📅 시작 날짜를 입력하세요 (YYYY-MM-DD 형식, 예: 2024-01-01):")
        start_date_input = input("시작 날짜: ").strip()
        if start_date_input:
            try:
                start_date = datetime.strptime(start_date_input, "%Y-%m-%d")
                print(f"✅ 시작 날짜: {start_date.strftime('%Y년 %m월 %d일')}")
            except ValueError:
                print("⚠️  잘못된 날짜 형식입니다. 날짜 필터를 사용하지 않습니다.")
                start_date = None
        
        print("\n📅 종료 날짜를 입력하세요 (YYYY-MM-DD 형식, 예: 2024-12-31):")
        end_date_input = input("종료 날짜: ").strip()
        if end_date_input:
            try:
                end_date = datetime.strptime(end_date_input, "%Y-%m-%d")
                print(f"✅ 종료 날짜: {end_date.strftime('%Y년 %m월 %d일')}")
            except ValueError:
                print("⚠️  잘못된 날짜 형식입니다. 종료 날짜를 사용하지 않습니다.")
                end_date = None
    
    # 파일명 설정
    print("\n📁 저장할 파일명을 입력하세요 (기본값: youtube_data.xlsx):")
    filename_input = input("파일명: ").strip()
    filename = filename_input if filename_input else "youtube_data.xlsx"
    
    if not filename.endswith('.xlsx'):
        filename += '.xlsx'
    
    print(f"\n🚀 크롤링을 시작합니다...")
    print(f"   - 키워드: {', '.join(keywords)}")
    print(f"   - 키워드당 영상 수: {videos_per_keyword}")
    print(f"   - 댓글 수집: {'예' if collect_comments else '아니오'}")
    if collect_comments:
        print(f"   - 영상당 댓글 수: {comments_per_video}")
    if use_date_filter:
        print(f"   - 수집 기간: {start_date.strftime('%Y년 %m월 %d일') if start_date else '제한없음'} ~ {end_date.strftime('%Y년 %m월 %d일') if end_date else '제한없음'}")
    print(f"   - 저장 파일: {filename}")
    
    # 크롤러 실행
    crawler = None
    try:
        crawler = YouTubeCrawler()
        
        # 영상 검색
        print(f"\n🔍 영상을 검색하고 있습니다...")
        videos = crawler.search_videos(keywords, videos_per_keyword, start_date, end_date)
        
        if not videos:
            print("❌ 검색된 영상이 없습니다.")
            return
        
        print(f"✅ {len(videos)}개의 영상을 찾았습니다.")
        
        # 댓글 수집
        all_comments = []
        if collect_comments and videos:
            print(f"\n💬 댓글을 수집하고 있습니다...")
            
            for i, video in enumerate(videos):
                if video.get('video_id'):
                    print(f"   진행률: {i+1}/{len(videos)} - {video['title'][:50]}...")
                    comments = crawler.get_video_comments(video['video_id'], comments_per_video)
                    all_comments.extend(comments)
        
        # 엑셀 저장
        print(f"\n💾 데이터를 엑셀 파일로 저장하고 있습니다...")
        saved_file = crawler.save_to_excel(videos, all_comments, filename)
        
        if saved_file:
            print(f"\n🎉 크롤링이 완료되었습니다!")
            print(f"📊 수집된 데이터:")
            print(f"   - 영상 수: {len(videos)}개")
            print(f"   - 댓글 수: {len(all_comments)}개")
            print(f"📁 저장 위치: {os.path.abspath(saved_file)}")
            
            # 데이터 미리보기
            print(f"\n📋 수집된 영상 미리보기:")
            for i, video in enumerate(videos[:5]):  # 처음 5개만 표시
                print(f"   {i+1}. {video['title'][:60]}...")
                print(f"      채널: {video['channel_name']}")
                print(f"      조회수: {video['view_count']}")
                print(f"      URL: {video['video_url']}")
                print()
            
            if len(videos) > 5:
                print(f"   ... 및 {len(videos) - 5}개 더")
        
    except KeyboardInterrupt:
        print("\n⚠️  사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류가 발생했습니다: {e}")
    finally:
        if crawler:
            crawler.close()
            print("🔒 브라우저가 종료되었습니다.")

if __name__ == "__main__":
    main() 