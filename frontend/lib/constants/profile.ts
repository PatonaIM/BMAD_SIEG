export const COMMON_SKILLS = [
  // Frontend
  "React",
  "Vue.js",
  "Angular",
  "TypeScript",
  "JavaScript",
  "HTML",
  "CSS",
  "Tailwind CSS",
  "Next.js",
  "Redux",
  
  // Backend
  "Node.js",
  "Python",
  "Java",
  "C#",
  "Go",
  "Ruby",
  "PHP",
  "Express.js",
  "Django",
  "Flask",
  "FastAPI",
  "Spring Boot",
  ".NET",
  
  // Database
  "PostgreSQL",
  "MySQL",
  "MongoDB",
  "Redis",
  "Elasticsearch",
  "SQL",
  "NoSQL",
  
  // DevOps & Cloud
  "Docker",
  "Kubernetes",
  "AWS",
  "Azure",
  "Google Cloud",
  "CI/CD",
  "Jenkins",
  "GitHub Actions",
  "Terraform",
  
  // Mobile
  "React Native",
  "Flutter",
  "iOS",
  "Android",
  "Swift",
  "Kotlin",
  
  // Other
  "Git",
  "REST APIs",
  "GraphQL",
  "Microservices",
  "Agile",
  "Scrum",
  "Testing",
  "Jest",
  "Cypress",
  "Machine Learning",
  "Data Science",
  "UI/UX Design",
]

export const JOB_TYPES = [
  { value: "permanent", label: "Permanent" },
  { value: "part_time", label: "Part Time" },
  { value: "contract", label: "Contract" },
] as const

export const POPULAR_LOCATIONS = [
  "Remote",
  "Philippines",
  "Australia",
  "India",
  "Sri Lanka",
  "Japan",
  "Korea",
  "Brazil",
  "United States",
  "United Kingdom",
  "Canada",
  "Singapore",
  "Germany",
  "Netherlands",
  "United Arab Emirates",
]

export const WORK_SETUPS = [
  { value: "remote", label: "Remote" },
  { value: "hybrid", label: "Hybrid" },
  { value: "onsite", label: "On-site" },
  { value: "any", label: "Any" },
] as const

export const CURRENCIES = [
  { value: "USD", label: "USD - US Dollar" },
  { value: "PHP", label: "PHP - Philippine Peso" },
  { value: "AUD", label: "AUD - Australian Dollar" },
  { value: "INR", label: "INR - Indian Rupee" },
  { value: "LKR", label: "LKR - Sri Lankan Rupee" },
  { value: "JPY", label: "JPY - Japanese Yen" },
  { value: "KRW", label: "KRW - South Korean Won" },
  { value: "BRL", label: "BRL - Brazilian Real" },
  { value: "EUR", label: "EUR - Euro" },
  { value: "GBP", label: "GBP - British Pound" },
  { value: "CAD", label: "CAD - Canadian Dollar" },
  { value: "SGD", label: "SGD - Singapore Dollar" },
  { value: "AED", label: "AED - UAE Dirham" },
] as const

// Salary is always annual for consistency across global markets
export const SALARY_PERIOD = "annually" as const
