export interface SecurityEvent {
  id: string;
  timestamp: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  title: string;
  // Non-core fields may be null for incomplete real-world records.
  description: string | null;
  assetHostname: string | null;
  assetIp: string | null;
  sourceIp: string | null;
  tags: string[];
}

// The user as returned by the API — never includes a password.
export interface User {
  id: string;
  email: string;
  role: string;
  status: string;
}
