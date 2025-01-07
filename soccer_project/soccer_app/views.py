# views.py
from django.shortcuts import render
from django.http import JsonResponse
from .models import Match
from datetime import datetime
import json
import requests
from django.db.models import Q

def load_data(request):
    url = "https://raw.githubusercontent.com/openfootball/football.json/master/2016-17/en.1.json"
    
    try:
        # Fetch data from URL
        response = requests.get(url)
        data = response.json()
        
        # Clear existing data
        Match.objects.all().delete()
        
        matches_created = 0
        
        # Process each round
        for round_data in data['rounds']:
            for match in round_data['matches']:
                try:
                    Match.objects.create(
                        date=datetime.strptime(match['date'], '%Y-%m-%d').date(),
                        home_team=match['team1'],  # Changed from match['team1']['name']
                        away_team=match['team2'],  # Changed from match['team2']['name']
                        home_score=match['score']['ft'][0],
                        away_score=match['score']['ft'][1],
                        round_name=round_data['name']
                    )
                    matches_created += 1
                except Exception as e:
                    print(f"Error creating match: {e}")
                    print(f"Match data: {match}")
        
        if matches_created > 0:
            return JsonResponse({
                "status": "success",
                "matches_loaded": matches_created,
                "message": f"Successfully loaded {matches_created} matches"
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": "No matches were loaded"
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"An error occurred: {str(e)}"
        }, status=500)

def home(request):
    # Get filter parameters
    team_filter = request.GET.get('team', '')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    # Start with all matches
    matches = Match.objects.all().order_by('date')  # Added ordering
    
    # Apply filters
    if team_filter:
        matches = matches.filter(
            Q(home_team__icontains=team_filter) |
            Q(away_team__icontains=team_filter)
        )
    
    if from_date:
        try:
            matches = matches.filter(date__gte=from_date)
        except ValueError:
            pass
            
    if to_date:
        try:
            matches = matches.filter(date__lte=to_date)
        except ValueError:
            pass
    
    # Add debug information
    context = {
        'matches': matches,
        'match_count': matches.count(),  # Add count for debugging
        'filters_applied': {
            'team': team_filter,
            'from_date': from_date,
            'to_date': to_date
        }
    }
    
    return render(request, 'soccer_app/home.html', context)


def api_standings(request):
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    
    matches = Match.objects.all()
    
    if from_date:
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
            matches = matches.filter(date__gte=from_date)
        except ValueError:
            return JsonResponse({"error": "Invalid from date format. Use YYYY-MM-DD"}, status=400)
            
    if to_date:
        try:
            to_date = datetime.strptime(to_date, '%Y-%m-%d')
            matches = matches.filter(date__lte=to_date)
        except ValueError:
            return JsonResponse({"error": "Invalid to date format. Use YYYY-MM-DD"}, status=400)
    
    standings = {}
    
    for match in matches:
        for team in [match.home_team, match.away_team]:
            if team not in standings:
                standings[team] = {
                    'team': team,
                    'played': 0,
                    'wins': 0,
                    'draws': 0,
                    'losses': 0,
                    'points': 0
                }
        
        standings[match.home_team]['played'] += 1
        standings[match.away_team]['played'] += 1
        
        if match.home_score > match.away_score:
            standings[match.home_team]['wins'] += 1
            standings[match.home_team]['points'] += 3
            standings[match.away_team]['losses'] += 1
        elif match.home_score < match.away_score:
            standings[match.away_team]['wins'] += 1
            standings[match.away_team]['points'] += 3
            standings[match.home_team]['losses'] += 1
        else:
            standings[match.home_team]['draws'] += 1
            standings[match.away_team]['draws'] += 1
            standings[match.home_team]['points'] += 1
            standings[match.away_team]['points'] += 1
    
    standings_list = list(standings.values())
    standings_list.sort(key=lambda x: (-x['points'], -x['wins']))
    
    for i, team in enumerate(standings_list, 1):
        team['place'] = i
    
    return JsonResponse(standings_list, safe=False)