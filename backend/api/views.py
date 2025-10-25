from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
import asyncio
from .analyze_feedback import AnalyzeFeedbackTool
# Create your views here.


@api_view(['GET'])
def get_bubble_data(request):
    async def run():
        tool = AnalyzeFeedbackTool(csv_path="api/data/unwrap_comments.csv")
        return await tool.execute()

    results = asyncio.run(run())

    # Transform into bubble heatmap format
    bubbles = []
    for item in results:
        bubbles.append({
            "id": item["theme"],
            "group": item["group"],
            "value": item["mentions"],          # bubble size
            "sentiment": item["sentiment"],     # color scale
            "quote": item["representative_quote"]
        })
    return Response(bubbles)
