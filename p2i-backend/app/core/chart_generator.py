"""
Chart Generation Utility for Prompt2Insight
Generates server-side chart images from product data using matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io
import base64
import logging
from typing import List, Dict, Any, Optional
import numpy as np

# Set matplotlib to use non-GUI backend
import matplotlib
matplotlib.use('Agg')

logger = logging.getLogger(__name__)

def generate_price_chart_image(products: List[Dict[str, Any]]) -> Optional[str]:
    """
    Generate a horizontal bar chart image for product price comparison
    
    Args:
        products: List of product dictionaries with name, price_value, price_display
        
    Returns:
        Base64 encoded PNG image string, or None if generation fails
    """
    try:
        if not products:
            logger.warning("No products provided for chart generation")
            return None
        
        # Filter products with valid prices
        valid_products = [
            p for p in products 
            if p.get('price_value') and isinstance(p.get('price_value'), (int, float)) and p.get('price_value') > 0
        ]
        
        if not valid_products:
            logger.warning("No products with valid prices found")
            return None
        
        # Sort products by price (ascending)
        valid_products.sort(key=lambda x: x['price_value'])
        
        # Extract data for plotting
        names = [p.get('name', 'Unknown')[:25] + ('...' if len(p.get('name', '')) > 25 else '') for p in valid_products]
        prices = [p['price_value'] for p in valid_products]
        price_displays = [p.get('price_display', f"₹{p['price_value']:,}") for p in valid_products]
        
        # Create figure with appropriate size
        fig, ax = plt.subplots(figsize=(12, max(6, len(valid_products) * 0.8)))
        
        # Color scheme - gradient from green (cheapest) to red (most expensive)
        colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(valid_products)))
        
        # Create horizontal bar chartvs
        bars = ax.barh(names, prices, color=colors, edgecolor='white', linewidth=1)
        
        # Customize the chart
        ax.set_xlabel('Price (₹)', fontsize=12, fontweight='bold')
        ax.set_title('Product Price Comparison', fontsize=16, fontweight='bold', pad=20)
        
        # Format x-axis to show currency
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
        
        # Add price labels on the bars
        for i, (bar, price_display) in enumerate(zip(bars, price_displays)):
            width = bar.get_width()
            ax.text(width + max(prices) * 0.01, bar.get_y() + bar.get_height()/2, 
                   price_display, ha='left', va='center', fontweight='bold', fontsize=10)
        
        # Adjust layout to prevent label cutoff
        plt.subplots_adjust(left=0.3, right=0.85, top=0.9, bottom=0.1)
        
        # Style improvements
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Remove top and right spines for cleaner look
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Add a subtle background
        ax.set_facecolor('#fafafa')
        fig.patch.set_facecolor('white')
        
        # Save plot to memory buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        
        # Encode to base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Clean up
        plt.close(fig)
        buffer.close()
        
        logger.info(f"Successfully generated price chart for {len(valid_products)} products")
        return image_base64
        
    except Exception as e:
        logger.error(f"Error generating price chart: {e}")
        return None

def generate_specs_chart_image(products: List[Dict[str, Any]]) -> Optional[str]:
    """
    Generate a radar/spider chart image for product specifications comparison
    
    Args:
        products: List of product dictionaries with name and specs
        
    Returns:
        Base64 encoded PNG image string, or None if generation fails
    """
    try:
        if not products:
            logger.warning("No products provided for specs chart generation")
            return None
        
        # Filter products with valid specs
        valid_products = []
        for p in products:
            specs = p.get('specs', {})
            if specs and any([
                specs.get('ram_gb', 0) > 0,
                specs.get('storage_gb', 0) > 0,
                specs.get('battery_mah', 0) > 0
            ]):
                valid_products.append(p)
        
        if not valid_products:
            logger.warning("No products with valid specs found")
            return None
        
        # Limit to first 4 products for readability
        valid_products = valid_products[:4]
        
        # Define spec categories
        categories = ['RAM (GB)', 'Storage (GB)', 'Battery (mAh)']
        
        # Prepare data
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Number of variables
        N = len(categories)
        
        # Angles for each category
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Complete the circle
        
        # Colors for different products
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA726', '#AB47BC']
        
        # Plot each product
        for i, product in enumerate(valid_products):
            specs = product.get('specs', {})
            
            # Extract spec values
            values = [
                specs.get('ram_gb', 0),
                specs.get('storage_gb', 0),
                specs.get('battery_mah', 0) / 100  # Scale down battery for better visualization
            ]
            values += values[:1]  # Complete the circle
            
            # Plot
            product_name = product.get('name', 'Unknown')[:20]
            ax.plot(angles, values, 'o-', linewidth=2, label=product_name, color=colors[i])
            ax.fill(angles, values, alpha=0.25, color=colors[i])
        
        # Customize the chart
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=12)
        ax.set_ylim(0, max([
            max([specs.get('ram_gb', 0) for specs in [p.get('specs', {}) for p in valid_products]]),
            max([specs.get('storage_gb', 0) for specs in [p.get('specs', {}) for p in valid_products]]),
            max([specs.get('battery_mah', 0) / 100 for specs in [p.get('specs', {}) for p in valid_products]])
        ]) * 1.1)
        
        # Add title
        plt.title('Product Specifications Comparison', size=16, fontweight='bold', y=1.08)
        
        # Add legend
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        # Add note about battery scaling
        plt.figtext(0.5, 0.02, '* Battery values scaled down by 100 for better visualization', 
                   ha='center', fontsize=10, style='italic')
        
        # Style improvements
        ax.grid(True, alpha=0.3)
        fig.patch.set_facecolor('white')
        
        # Save plot to memory buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        
        # Encode to base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Clean up
        plt.close(fig)
        buffer.close()
        
        logger.info(f"Successfully generated specs chart for {len(valid_products)} products")
        return image_base64
        
    except Exception as e:
        logger.error(f"Error generating specs chart: {e}")
        return None
