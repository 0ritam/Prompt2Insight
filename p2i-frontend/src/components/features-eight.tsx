import { Card } from '~/components/ui/card'
import { CalendarCheck, Layout, Sparkles, Target, BarChart3, Search } from 'lucide-react'
import Image from 'next/image'

export default function FeaturesSection() {
    return (
        <section>
            <div className="py-4">
                <div className="mx-auto w-full max-w-5xl px-6">
                    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                        <Card
                            className="col-span-full overflow-hidden pl-6 pt-6 bg-gray-100 dark:bg-gray-900/50">
                            <BarChart3 className="text-primary size-5" />
                            <h3 className="text-foreground mt-5 text-lg font-semibold">AI-Powered Product Analysis</h3>
                            <p className="text-muted-foreground mt-3 max-w-xl text-balance">Transform your product research with intelligent insights and visualizations. Compare products, analyze specifications, and get AI-curated recommendations instantly.</p>
                            <div className="mask-b-from-95% -ml-2 -mt-2 mr-0.5 pl-2 pt-2">
                                <div className="bg-background rounded-tl-(--radius) ring-foreground/5 relative mx-auto mt-8 h-96 overflow-hidden border border-transparent shadow ring-1">
                                    <Image
                                        src="/feature1.png"
                                        alt="Prompt2Insight Features"
                                        width="2880"
                                        height="1842"
                                        className="object-top-left h-full object-cover"
                                    />
                                </div>
                            </div>
                        </Card>
                        <Card
                            className="p-6 bg-gray-100 dark:bg-gray-900/50">
                            <Search className="text-primary size-5" />
                            <h3 className="text-foreground mt-5 text-lg font-semibold">Smart Product Discovery</h3>
                            <p className="text-muted-foreground mt-3 text-balance">Find the perfect products with AI-driven search and intelligent filtering based on your specific needs.</p>
                        </Card>

                        <Card
                            className="p-6 bg-gray-100 dark:bg-gray-900/50">
                            <BarChart3 className="text-primary size-5" />
                            <h3 className="text-foreground mt-5 text-lg font-semibold">Interactive Data Visualization</h3>
                            <p className="text-muted-foreground mt-3 text-balance">Generate dynamic charts and graphs to visualize price comparisons, specifications, and market trends.</p>
                        </Card>
                        <Card
                            className="p-6 bg-gray-100 dark:bg-gray-900/50">
                            <Sparkles className="text-primary size-5" />
                            <h3 className="text-foreground mt-5 text-lg font-semibold">AI-Curated Insights</h3>
                            <p className="text-muted-foreground mt-3 text-balance">Get personalized recommendations and insights based on comprehensive product analysis and market intelligence.</p>
                        </Card>
                    </div>
                </div>
            </div>
        </section>
    )
}
