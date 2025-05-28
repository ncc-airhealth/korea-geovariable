
export default {
  landing: {
    hero: {
      title: '한국 지리변수 API 테스팅 포털',
      description: '한국 도시 지역의 지리변수를 테스트하고 검증하기 위한 종합 플랫폼입니다.'
    },
    buttons: {
      getStarted: '시작하기',
      apiPortal: 'API 포털 접속'
    },
    features: {
      title: '주요 기능',
      borderCalculations: {
        title: '경계 기반 계산',
        description: '시군구, 읍면동 및 사용자 지정 연구 그리드를 포함한 행정 경계를 기반으로 다양한 지리공간 변수를 계산합니다.'
      },
      dataCategories: {
        title: '다양한 데이터 카테고리',
        description: '지리적 특징, 교통 지표, 거리 계산, 환경 데이터 및 의료 정보에 접근할 수 있습니다.'
      },
      testValidate: {
        title: '테스트 및 검증',
        description: '다양한 매개변수로 API 엔드포인트를 쉽게 테스트하고 검증 및 분석을 위한 구조화된 결과를 확인할 수 있습니다.'
      }
    },
    apiCategories: {
      title: '사용 가능한 API 카테고리',
      description: '다양한 지리공간 API를 탐색해보세요',
      geographic: '지리적 특징',
      transport: '교통',
      distance: '거리',
      environmental: '환경',
      healthcare: '의료',
      apiCount: 'API {{count}}개'
    },
    documentation: {
      title: '종합 API 테스트',
      description: '직관적인 인터페이스를 통해 연구자와 개발자가 한국 도시 지역의 지리공간 계산을 검증할 수 있습니다.'
    },
    footer: {
      copyright: '© {{year}} 한국 지리변수 API 테스팅 포털',
      subtitle: '국립암센터 / 대기건강연구'
    }
  },
  header: {
    title: '한국 지리변수',
    subtitle: 'API 테스팅 포털',
    signIn: '로그인',
    signUp: '회원가입',
    signOut: '로그아웃'
  },
  auth: {
    title: '한국 지리변수',
    subtitle: 'API 테스팅 포털',
    email: '이메일',
    password: '비밀번호',
    signIn: {
      title: '로그인',
      button: '로그인',
      loading: '로그인 중...'
    },
    signUp: {
      title: '회원가입',
      button: '회원가입',
      loading: '회원가입 중...'
    }
  },
  dashboard: {
    apiEndpoints: 'API 엔드포인트',
    testParameters: '테스트 매개변수',
    borderType: '경계 유형',
    year: '연도',
    selectedEndpoints: '선택된 엔드포인트',
    runTests: '테스트 실행',
    runningTests: '테스트 실행 중...',
    testResults: '테스트 결과',
    activeTabs: '활성 테스트',
    completedTabs: '완료된 테스트',
    noActiveTests: '활성 테스트 없음',
    noCompletedTests: '완료된 테스트 없음',
    waiting: '대기 중...',
    refresh: '새로고침',
    hide: '숨기기',
    view: '보기',
    result: '결과:',
    borderTypes: {
      sgg: '시군구 (도시/군/구)',
      emd: '읍면동 (읍/면/동)',
      jgg: '사용자 지정 연구 그리드'
    },
    emissionNote: '참고: 배출량 데이터는 2001, 2005, 2010, 2015, 2019년도에만 사용 가능합니다.'
  },
  common: {
    endpoint: '엔드포인트',
    parameters: '매개변수',
    status: '상태',
    started: '시작됨',
    completed: '완료됨',
    unknown: '알 수 없음',
    success: '성공',
    failed: '실패',
    running: '실행 중',
    border: '경계',
    year: '연도'
  },
  languageSwitcher: {
    en: '영어',
    ko: '한국어'
  }
};
