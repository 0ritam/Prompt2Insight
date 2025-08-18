import { Card } from '~/components/ui/card'
import * as React from 'react'
import { Gemini,NextJS, LangChain, ShadcnUI, Python, OAuth } from '~/components/logos'

export default function Integrations() {
    return (
        <section>
            <div className="py-32">
                <div className="mx-auto max-w-5xl px-6">
                    <div>
                        <h2 className="text-balance text-3xl font-semibold md:text-4xl">Built with modern technologies</h2>
                        <p className="text-muted-foreground mt-3 text-lg">Powered by cutting-edge tools and frameworks for optimal performance and scalability.</p>
                    </div>

                    <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                        <IntegrationCard
                            title="Google Gemini"
                            description="Advanced AI language model providing intelligent insights and analysis capabilities for enhanced user experiences.">
                            <Gemini />
                        </IntegrationCard>

                        <IntegrationCard
                            title="Next.js"
                            description="React framework for production with server-side rendering, static generation, and optimal performance.">
                            <NextJS />
                        </IntegrationCard>

                        <IntegrationCard
                            title="LangChain"
                            description="Framework for developing applications powered by language models with advanced AI orchestration.">
                            <LangChain />
                        </IntegrationCard>

                        <IntegrationCard
                            title="Shadcn/UI"
                            description="Beautifully designed components built with Radix UI and Tailwind CSS for modern web applications.">
                            <ShadcnUI />
                        </IntegrationCard>

                        <IntegrationCard
                            title="Python"
                            description="Powerful backend development with robust data processing and AI/ML capabilities for analytics.">
                            <Python />
                        </IntegrationCard>

                        <IntegrationCard
                            title="OAuth"
                            description="Secure authentication and authorization framework ensuring safe user access and data protection.">
                            <OAuth />
                        </IntegrationCard>
                    </div>
                </div>
            </div>
        </section>
    )
}

const IntegrationCard = ({ title, description, children, link = 'https://github.com/meschacirung/cnblocks' }: { title: string; description: string; children: React.ReactNode; link?: string }) => {
    return (
        <Card
            className="p-6 bg-gray-50 dark:bg-gray-900/50">
            <div className="relative">
                <div className="*:size-10">{children}</div>

                <div className="mt-6 space-y-1.5">
                    <h3 className="text-lg font-semibold">{title}</h3>
                    <p className="text-muted-foreground line-clamp-2">{description}</p>
                </div>
            </div>
        </Card>
    )
}
