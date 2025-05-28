
export default {
  landing: {
    hero: {
      title: 'Korea GeoVariable API Testing Portal',
      description: 'A comprehensive platform for testing and validating geospatial variables for Korean urban areas.'
    },
    buttons: {
      getStarted: 'Get Started',
      apiPortal: 'Access API Portal'
    },
    features: {
      title: 'Key Features',
      borderCalculations: {
        title: 'Border Based Calculations',
        description: 'Calculate various geospatial variables based on administrative borders including Sigungu, Eup/Myeon/Dong, and custom research grids.'
      },
      dataCategories: {
        title: 'Multiple Data Categories',
        description: 'Access geographical features, transport metrics, distance calculations, environmental data, and healthcare information.'
      },
      testValidate: {
        title: 'Test & Validate',
        description: 'Easily test API endpoints with different parameters and view structured results for validation and analysis.'
      }
    },
    apiCategories: {
      title: 'Available API Categories',
      description: 'Explore our comprehensive range of geospatial APIs',
      geographic: 'Geographic Features',
      transport: 'Transport',
      distance: 'Distance',
      environmental: 'Environmental',
      healthcare: 'Healthcare',
      apiCount: '{{count}} APIs'
    },
    documentation: {
      title: 'Comprehensive API Testing',
      description: 'Our platform allows researchers and developers to validate geospatial calculations for Korean urban areas through an intuitive interface.'
    },
    footer: {
      copyright: '© {{year}} Korea GeoVariable API Testing Portal',
      subtitle: 'National Cancer Center / Air Health Research'
    }
  },
  header: {
    title: 'Korea GeoVariable',
    subtitle: 'API Testing Portal',
    signIn: 'Sign In',
    signUp: 'Sign Up',
    signOut: 'Sign Out'
  },
  auth: {
    title: 'Korea GeoVariable',
    subtitle: 'API Testing Portal',
    email: 'Email',
    password: 'Password',
    signIn: {
      title: 'Sign In',
      button: 'Sign In',
      loading: 'Signing In...'
    },
    signUp: {
      title: 'Sign Up',
      button: 'Sign Up',
      loading: 'Signing Up...'
    }
  },
  dashboard: {
    apiEndpoints: 'API Endpoints',
    testParameters: 'Test Parameters',
    borderType: 'Border Type',
    year: 'Year',
    selectedEndpoints: 'Selected Endpoints',
    runTests: 'Run Tests',
    runningTests: 'Running Tests...',
    testResults: 'Test Results',
    activeTabs: 'Active Tests',
    completedTabs: 'Completed Tests',
    noActiveTests: 'No active tests',
    noCompletedTests: 'No completed tests',
    waiting: 'Waiting...',
    refresh: 'Refresh',
    hide: 'Hide',
    view: 'View',
    result: 'Result:',
    borderTypes: {
      sgg: 'Sigungu (City/County/District)',
      emd: 'Eup/Myeon/Dong (Town/Township/Neighborhood)',
      jgg: 'Custom Research Grid'
    },
    emissionNote: 'Note: Emission data is only available for years 2001, 2005, 2010, 2015, and 2019.'
  },
  common: {
    endpoint: 'Endpoint',
    parameters: 'Parameters',
    status: 'Status',
    started: 'Started',
    completed: 'Completed',
    unknown: 'Unknown',
    success: 'Success',
    failed: 'Failed',
    running: 'Running',
    border: 'Border',
    year: 'Year'
  },
  languageSwitcher: {
    en: 'English',
    ko: 'Korean'
  }
};
