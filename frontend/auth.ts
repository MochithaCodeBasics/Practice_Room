import NextAuth from "next-auth";

async function refreshAccessToken(token: Record<string, unknown>) {
  try {
    const response = await fetch(
      `${process.env.CODEBASICS_BASE_URL}/oauth/token`,
      {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
          grant_type: "refresh_token",
          refresh_token: token.refreshToken as string,
          client_id: process.env.AUTH_CODEBASICS_ID!,
          client_secret: process.env.AUTH_CODEBASICS_SECRET!,
        }),
      }
    );

    const refreshed = await response.json();
    if (!response.ok) throw new Error(refreshed.error ?? "refresh_failed");

    // Compute new expiresAt — prefer provider's expires_at, fall back to
    // current time + expires_in (default 15 days per Codebasics spec).
    const expiresAt = refreshed.expires_at
      ? Math.floor(Number(refreshed.expires_at))
      : Math.floor(Date.now() / 1000) + (Number(refreshed.expires_in) || 15 * 24 * 3600);

    return {
      ...token,
      accessToken: refreshed.access_token,
      refreshToken: refreshed.refresh_token ?? token.refreshToken, // keep old if not rotated
      expiresAt,
      error: undefined,
    };
  } catch (err) {
    console.error("[Auth] Token refresh failed:", err);
    return { ...token, error: "RefreshAccessTokenError" as const };
  }
}

export const { handlers, signIn, signOut, auth } = NextAuth({
  trustHost: true,
  providers: [
    {
      id: "codebasics",
      name: "Codebasics",
      type: "oauth",
      authorization: {
        url: `${process.env.CODEBASICS_BASE_URL}/oauth/authorize?scope=read-user&response_type=code`,
      },
      token: `${process.env.CODEBASICS_BASE_URL}/oauth/token`,
      userinfo: `${process.env.CODEBASICS_BASE_URL}/api/user`,
      clientId: process.env.AUTH_CODEBASICS_ID!,
      clientSecret: process.env.AUTH_CODEBASICS_SECRET!,
      profile(profile) {
        return {
          id: profile.id.toString(),
          name: profile.full_name || profile.name,
          email: profile.email,
          image: profile.avatar,
          role: profile.role_name,
        };
      },
    },
  ],
  callbacks: {
    async jwt({ token, account, profile }) {
      // ── Initial sign-in: store raw OAuth tokens ────────────────────────────
      if (account) {
        token.accessToken = account.access_token;
        token.refreshToken = account.refresh_token;
        token.expiresAt = account.expires_at;
        token.error = undefined;
      }
      if (profile) {
        const p = profile as Record<string, unknown>;
        token.userId = (p.id as number)?.toString();
        token.userRole = p.role_name as string;
        token.userEmail = p.email as string;
        token.userName = (p.full_name as string) || (p.name as string);
        token.userImage = p.avatar as string;
        token.userIsAdmin = p.is_admin as boolean;
      }

      // ── No expiry info → assume valid (provider didn't supply it) ──────────
      if (!token.expiresAt) return token;

      // ── Access token still valid (refresh 5 min before expiry) ────────────
      if (Date.now() < (token.expiresAt as number) * 1000 - 5 * 60 * 1000) {
        return token;
      }

      // ── Token expired → attempt refresh ───────────────────────────────────
      if (token.refreshToken) {
        return refreshAccessToken(token as Record<string, unknown>);
      }

      return token;
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken as string;
      session.error = token.error as string | undefined;
      session.user.id = (token.userId as string) || session.user.id;
      session.user.role = (token.userRole as string) || session.user.role;
      session.user.email = (token.userEmail as string) || session.user.email;
      session.user.name = (token.userName as string) || session.user.name;
      session.user.image = (token.userImage as string) || session.user.image;
      session.user.isAdmin = token.userIsAdmin as boolean | undefined;
      return session;
    },
  },
  session: {
    strategy: "jwt",
    maxAge: 48 * 60 * 60, // 48 hours
  },
  pages: {
    signIn: "/",
  },
  debug: process.env.NODE_ENV === "development",
});
