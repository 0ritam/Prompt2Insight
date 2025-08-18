"use client";

import React from "react";
import { TrendingUp } from "lucide-react";
import { Bar, BarChart, CartesianGrid, LabelList, XAxis, YAxis, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Legend, ResponsiveContainer, Tooltip } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "~/components/ui/card";

// Define a clear type for the incoming product data
interface Product {
  name: string;
  price_value: number;
  price_display: string;
  specs: {
    ram_gb: number;
    storage_gb: number;
    battery_mah: number;
  };
}

interface ProductChartProps {
  data: Product[];
  chartType: 'price' | 'specs';
}

export function ProductChart({ data, chartType }: ProductChartProps) {
  // Debug logging to see what data we're receiving
  console.log('🔍 ProductChart Debug:');
  console.log('- Data received:', data);
  console.log('- Data length:', data?.length);
  console.log('- Chart type:', chartType);
  console.log('- First product sample:', data?.[0]);
  
  if (!data || data.length === 0) {
    console.log('❌ No data available for chart');
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-64">
          <p className="text-gray-500">No data available for visualization.</p>
        </CardContent>
      </Card>
    );
  }

  // --- PRICE CHART IMPLEMENTATION ---
  if (chartType === 'price') {
    console.log('📊 Processing Price Chart');
    
    // Filter out products with no valid price and map to the correct format
    const priceData = data
      .filter(p => {
        console.log(`- Checking price for ${p.name}: ${p.price_value}`);
        return p.price_value > 0;
      })
      .map(p => ({
        name: p.name.length > 20 ? `${p.name.substring(0, 20)}...` : p.name,
        fullName: p.name,
        price: p.price_value,
        priceDisplay: p.price_display
      }));

    console.log('📈 Final price data:', priceData);
    console.log('📈 Price data length:', priceData.length);

    if (priceData.length === 0) {
      console.log('❌ No valid price data found');
      return (
        <Card>
          <CardContent className="flex items-center justify-center h-64">
            <p className="text-gray-500">No valid price data to display.</p>
          </CardContent>
        </Card>
      );
    }

    console.log('✅ Rendering price chart with', priceData.length, 'products');

    return (
      <Card>
        <CardHeader>
          <CardTitle>Price Comparison</CardTitle>
          <p className="text-sm text-muted-foreground">Comparing {priceData.length} products</p>
        </CardHeader>
        <CardContent>
          <div style={{ width: '100%', height: '400px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={priceData}
                layout="vertical"
                margin={{ top: 20, right: 80, left: 20, bottom: 20 }}
              >
                <CartesianGrid horizontal={false} strokeDasharray="3 3" stroke="#e0e0e0" />
                <YAxis
                  dataKey="name"
                  type="category"
                  tickLine={false}
                  tickMargin={10}
                  axisLine={false}
                  tick={{ fontSize: 12 }}
                  width={150}
                />
                <XAxis 
                  type="number" 
                  hide
                />
                <Tooltip
                  formatter={(value) => [`₹${Number(value).toLocaleString()}`, 'Price']}
                  labelFormatter={(label) => label}
                />
                <Bar
                  dataKey="price"
                  fill="#3b82f6"
                  radius={4}
                  isAnimationActive={false}
                  minPointSize={5}
                >
                  <LabelList
                    dataKey="priceDisplay"
                    position="right"
                    offset={8}
                    className="fill-foreground"
                    fontSize={12}
                  />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    );
  }

  // --- SPECS CHART IMPLEMENTATION ---
  if (chartType === 'specs') {
    console.log('🎯 Processing Specs Chart');
    console.log('🎯 Raw data for specs:', data);
    
    // Recharts RadarChart needs data structured by spec, not by product.
    const specsForChart = [
      { spec: 'RAM (GB)' },
      { spec: 'Storage (GB)' },
      { spec: 'Battery (mAh)' },
    ];

    // Add each product's value to the spec objects
    const radarData = specsForChart.map(s => {
        const entry: { [key: string]: any } = { spec: s.spec };
        data.forEach(p => {
            console.log(`- Processing ${p.name} specs:`, p.specs);
            const productName = p.name.length > 15 ? `${p.name.substring(0, 15)}...` : p.name;
            if (s.spec === 'RAM (GB)') entry[productName] = p.specs.ram_gb || 0;
            if (s.spec === 'Storage (GB)') entry[productName] = p.specs.storage_gb || 0;
            if (s.spec === 'Battery (mAh)') entry[productName] = p.specs.battery_mah || 0;
        });
        return entry;
    });
    
    console.log('🎯 Final radar data:', radarData);
    
    // Check if we have any meaningful spec data
    const hasValidSpecs = data.some(p => {
      console.log(`- Checking specs for ${p.name}:`, p.specs);
      return p.specs && (p.specs.ram_gb > 0 || p.specs.storage_gb > 0 || p.specs.battery_mah > 0);
    });

    console.log('🎯 Has valid specs:', hasValidSpecs);

    if (!hasValidSpecs) {
       console.log('❌ No valid specs data found');
       return (
         <Card>
           <CardContent className="flex items-center justify-center h-64">
             <p className="text-gray-500">No valid specification data to display.</p>
           </CardContent>
         </Card>
       );
    }
    
    console.log('✅ Rendering specs chart with', data.length, 'products');
    
    const colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6'];

    return (
      <Card>
        <CardHeader>
          <CardTitle>Specifications Comparison</CardTitle>
          <p className="text-sm text-muted-foreground">Comparing specifications across {data.length} products</p>
        </CardHeader>
        <CardContent>
          <div style={{ width: '100%', height: '400px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="spec" />
                <PolarRadiusAxis />
                <Tooltip 
                  formatter={(value, name) => [value, name]}
                  labelFormatter={(label) => `Spec: ${label}`}
                />
                <Legend />
                {data.map((product, index) => {
                  const productName = product.name.length > 15 ? `${product.name.substring(0, 15)}...` : product.name;
                  console.log(`🎯 Adding radar for ${productName} with dataKey: ${productName}`);
                  return (
                    <Radar 
                      key={product.name}
                      name={productName} 
                      dataKey={productName} 
                      stroke={colors[index % colors.length]} 
                      fill={colors[index % colors.length]} 
                      fillOpacity={0.1}
                      isAnimationActive={false}
                    />
                  )
                })}
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    );
  }

  return null;
}
