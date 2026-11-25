from fastapi import APIRouter, Depends
from backend.schemas.schemas import SearchRequest, SearchResponse, SearchResultItem
from backend.tools.tavily_tool import tavily_tool

router = APIRouter(prefix="/search", tags=["Search"])

@router.post("", response_model=SearchResponse)
def search_places(req: SearchRequest):
    results = tavily_tool.search(req.query)
    formatted = [
        SearchResultItem(
            title=item["title"],
            snippet=item["snippet"],
            url=item.get("url"),
            source=item.get("source")
        ) for item in results
    ]
    return SearchResponse(query=req.query, results=formatted)
