import { DefaultSession } from "next-auth";

declare module "next-auth" {
  interface Session {
    accessToken?: string;
    /** Set to "RefreshAccessTokenError" when the OAuth refresh fails. */
    error?: string;
    user: {
      id: string;
      role?: string;
      isAdmin?: boolean;
    } & DefaultSession["user"];
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    accessToken?: string;
    refreshToken?: string;
    expiresAt?: number;
    /** Set to "RefreshAccessTokenError" when the OAuth refresh fails. */
    error?: string;
    codebasicsProfile?: Record<string, unknown>;
    userIsAdmin?: boolean;
  }
}
