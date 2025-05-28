
import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import Header from '@/components/Header';
import { ArrowRight, Code, LayoutDashboard, Server, CheckCircle } from 'lucide-react';
import { useTranslation } from 'react-i18next';

const Landing = () => {
  const { t } = useTranslation();
  
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1">
        {/* Hero Section */}
        <section className="bg-gradient-to-b from-background to-secondary/20 py-20">
          <div className="container mx-auto px-4 text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">{t('landing.hero.title')}</h1>
            <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-3xl mx-auto">
              {t('landing.hero.description')}
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Button asChild size="lg" className="gap-2">
                <Link to="/auth">
                  {t('landing.buttons.getStarted')} <ArrowRight />
                </Link>
              </Button>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-16 bg-background">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-bold mb-12 text-center">{t('landing.features.title')}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              <FeatureCard 
                icon={<Server />}
                title={t('landing.features.borderCalculations.title')}
                description={t('landing.features.borderCalculations.description')}
              />
              <FeatureCard 
                icon={<LayoutDashboard />}
                title={t('landing.features.dataCategories.title')}
                description={t('landing.features.dataCategories.description')}
              />
              <FeatureCard 
                icon={<CheckCircle />}
                title={t('landing.features.testValidate.title')}
                description={t('landing.features.testValidate.description')}
              />
            </div>
          </div>
        </section>

        {/* API Categories Section */}
        <section className="py-16 bg-secondary/20">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-bold mb-2 text-center">{t('landing.apiCategories.title')}</h2>
            <p className="text-center text-muted-foreground mb-12">{t('landing.apiCategories.description')}</p>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              <CategoryCard title={t('landing.apiCategories.geographic')} count={3} />
              <CategoryCard title={t('landing.apiCategories.transport')} count={3} />
              <CategoryCard title={t('landing.apiCategories.distance')} count={4} />
              <CategoryCard title={t('landing.apiCategories.environmental')} count={3} />
              <CategoryCard title={t('landing.apiCategories.healthcare')} count={2} />
            </div>
          </div>
        </section>

        {/* Documentation Section */}
        <section className="py-16 bg-background">
          <div className="container mx-auto px-4 text-center">
            <h2 className="text-3xl font-bold mb-4">{t('landing.documentation.title')}</h2>
            <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
              {t('landing.documentation.description')}
            </p>
            <Button asChild variant="outline" size="lg" className="gap-2">
              <Link to="/auth">
                <Code className="mr-2" /> {t('landing.buttons.apiPortal')}
              </Link>
            </Button>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-secondary py-8">
        <div className="container mx-auto px-4">
          <div className="text-center">
            <p className="text-muted-foreground">
              {t('landing.footer.copyright', { year: new Date().getFullYear() })}
            </p>
            <p className="text-sm text-muted-foreground mt-2">
              {t('landing.footer.subtitle')}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

// Feature Card Component
const FeatureCard = ({ icon, title, description }: { icon: React.ReactNode, title: string, description: string }) => (
  <Card className="h-full">
    <CardContent className="pt-6">
      <div className="bg-primary/10 p-3 rounded-full w-fit mb-4 text-primary">
        {icon}
      </div>
      <h3 className="font-bold text-xl mb-2">{title}</h3>
      <p className="text-muted-foreground">{description}</p>
    </CardContent>
  </Card>
);

// Category Card Component
const CategoryCard = ({ title, count }: { title: string, count: number }) => {
  const { t } = useTranslation();
  
  return (
    <Card className="bg-card/50 hover:bg-card/80 transition-colors cursor-default">
      <CardContent className="py-4 px-5 flex justify-between items-center">
        <h4 className="font-medium">{title}</h4>
        <span className="bg-primary/10 text-primary py-1 px-2 rounded-full text-sm">
          {t('landing.apiCategories.apiCount', { count })}
        </span>
      </CardContent>
    </Card>
  );
};

export default Landing;
