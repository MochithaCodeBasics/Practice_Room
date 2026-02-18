import NextAuth from "next-auth";

export const { handlers, signIn, signOut, auth } = NextAuth({
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
      if (account) {
        token.accessToken = account.access_token;
        token.refreshToken = account.refresh_token;
        token.expiresAt = account.expires_at;
      }
      if (profile) {
        const p = profile as Record<string, unknown>;
        token.userId = (p.id as number)?.toString();
        token.userRole = p.role_name as string;
        token.userEmail = p.email as string;
        token.userName = (p.full_name as string) || (p.name as string);
        token.userImage = p.avatar as string;
      }
      return token;
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken as string;
      session.user.id = (token.userId as string) || session.user.id;
      session.user.role = (token.userRole as string) || session.user.role;
      session.user.email = (token.userEmail as string) || session.user.email;
      session.user.name = (token.userName as string) || session.user.name;
      session.user.image = (token.userImage as string) || session.user.image;
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
