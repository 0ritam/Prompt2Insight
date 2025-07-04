"use client";

import React, { useState } from "react";
import { useGoogleSearch } from "~/hooks/useGoogleSearch";
import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";
import { Badge } from "~/components/ui/badge";
import { ExternalLink, Search } from "lucide-react";

export function GoogleSearchDemo() {
  const [query, setQuery] = useState("");
  const { searchProducts, isLoading, error, results } = useGoogleSearch();

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    try {
      await searchProducts(query.trim());
    } catch (error) {
      console.error("Search failed:", error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Input */}
      <div className="flex gap-2">
        <Input
          placeholder="Search for products... (e.g., 'iPhone 15', 'gaming laptop')"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
        />
        <Button 
          onClick={handleSearch} 
          disabled={isLoading || !query.trim()}
          className="gap-2"
        >
          <Search className="h-4 w-4" />
          {isLoading ? "Searching..." : "Search"}
        </Button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}

      {/* Results Display */}
      {results.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">
            Search Results ({results.length} found)
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {results.map((result, index) => (
              <Card key={index} className="h-full flex flex-col">
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-start gap-2">
                    <CardTitle className="text-sm line-clamp-2">
                      {result.title}
                    </CardTitle>
                    <Badge variant="outline" className="text-xs">
                      Google
                    </Badge>
                  </div>
                </CardHeader>
                
                <CardContent className="flex-1 flex flex-col">
                  {/* Image */}
                  {result.image && (
                    <div className="relative w-full aspect-square mb-3 bg-muted/30 rounded-md overflow-hidden">
                      <img 
                        src={result.image} 
                        alt={result.title}
                        className="object-cover w-full h-full"
                        onError={(e) => {
                          const target = e.target as HTMLImageElement;
                          target.style.display = 'none';
                        }}
                      />
                    </div>
                  )}
                  
                  {/* Description */}
                  {result.description && (
                    <p className="text-xs text-muted-foreground mb-3 line-clamp-3 flex-1">
                      {result.description}
                    </p>
                  )}
                  
                  {/* View Product Button */}
                  {result.url && (
                    <Button 
                      variant="outline" 
                      size="sm"
                      className="w-full gap-1 mt-auto"
                      onClick={() => window.open(result.url, '_blank')}
                    >
                      View Product <ExternalLink className="h-3 w-3" />
                    </Button>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* No Results Message */}
      {!isLoading && !error && results.length === 0 && query && (
        <div className="text-center py-8 text-muted-foreground">
          <p>No results found. Try a different search term.</p>
        </div>
      )}
    </div>
  );
}
