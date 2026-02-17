import NextAuth from "next-auth";

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    {
      id: "codebasics",
      name: "Codebasics",
      type: "oauth",
      authorization: {
        url: `${process.env.CODEBASICS_BASE_URL}/oauth/authorize`,
        params: {
          scope: "read-user",
          response_type: "code",
        },
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
      if (account) {
        token.accessToken = account.access_token;
        token.refreshToken = account.refresh_token;
        token.expiresAt = account.expires_at;
      }
      if (profile) {
        token.codebasicsProfile = profile;
      }
      return token;
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken as string;
      if (token.codebasicsProfile) {
        const profile = token.codebasicsProfile as Record<string, unknown>;
        session.user.id = (profile.id as number)?.toString() || session.user.id;
        session.user.role = profile.role_name as string;
      }
      return session;
    },
  },
  pages: {
    signIn: "/",
  },
  debug: process.env.NODE_ENV === "development",
});
