---
name: login-with-codebasics
description: Help users integrate "Login with Codebasics" OAuth authentication in their Next.js applications. Use when users want to set up Codebasics OAuth, create Auth.js configuration, implement login flows, or troubleshoot authentication issues.
---

# Login with Codebasics - OAuth Integration Skill

This skill helps users integrate "Login with Codebasics" OAuth authentication in Next.js applications using Auth.js (NextAuth v5).

## When to Use This Skill

Trigger this skill when users:
- Want to integrate Codebasics OAuth authentication
- Need to set up "Login with Codebasics" in their Next.js app
- Ask about Auth.js configuration for Codebasics
- Need help with OAuth setup, token handling, or user data access
- Are troubleshooting Codebasics authentication issues
- Want to implement social login with Codebasics

## Core Knowledge

### OAuth Configuration

**Codebasics OAuth Endpoints:**
- Authorization: `https://codebasics.io/oauth/authorize`
- Token: `https://codebasics.io/oauth/token`
- User Info: `https://codebasics.io/api/user`
- OAuth Client Portal: `https://codebasics.io/panel/developer/oauth-clients`

**OAuth Flow:**
- Type: OAuth 2.0 Authorization Code Flow
- Scope: `read-user`
- Provider ID: `codebasics`
- Direct redirect (no separate login form needed)

**Token Lifetimes:**
- Access Token: 15 days
- Refresh Token: 30 days

**Callback URL Format:**
- Development: `http://localhost:3000/api/auth/callback/codebasics`
- Production: `https://yourdomain.com/api/auth/callback/codebasics`

### Prerequisites

- Next.js application with App Router
- Node.js 18+
- Codebasics account
- OAuth credentials (Client ID and Client Secret) from Codebasics Developer Portal

## Integration Approach

### CRITICAL: Always Create Actual Files

**This skill MUST create actual files using the `create_file` tool.** Do not just show code snippets - generate complete, working files that users can immediately use.

### Step 1: Understand User's Needs

Ask clarifying questions to understand:
1. Are they starting from scratch or adding to an existing app?
2. Do they already have OAuth credentials from Codebasics?
3. Are they using TypeScript or JavaScript?
4. Are they using App Router or Pages Router? (Skill focuses on App Router)
5. Do they need full setup or help with a specific issue?
6. What is their project structure? (to determine correct file paths)

### Step 2: Create Configuration Files

**IMPORTANT**: Use `create_file` tool to generate actual files. Create files in `/home/claude/` and then provide them to the user.

When users need setup, create these actual files:

#### File 1: Environment Variables (`.env.local`)

**Create this file using `create_file`:**

```typescript
create_file(
  path: "/home/claude/.env.local",
  file_text: `# Auth.js Secret (generate using: openssl rand -base64 32)
AUTH_SECRET="[GENERATE_THIS_BY_RUNNING: openssl rand -base64 32]"

# Codebasics OAuth Credentials (from https://codebasics.io/panel/developer/oauth-clients)
AUTH_CODEBASICS_ID="your-client-id-here"
AUTH_CODEBASICS_SECRET="your-client-secret-here"

# Base URLs
CODEBASICS_BASE_URL="https://codebasics.io"
NEXT_PUBLIC_APP_URL="http://localhost:3000"
`
)
```

**After creating the file:**
- Tell user to replace `your-client-id-here` and `your-client-secret-here` with their actual credentials
- Remind them to generate AUTH_SECRET by running: `openssl rand -base64 32`
- Emphasize: NEVER commit this file to version control (add to .gitignore)

#### File 2: Auth Configuration (`auth.ts`)

**IMPORTANT**: Create this file in the project root (not in `app/` directory).

**When to use Quick vs Full setup:**
- **Quick**: User just wants basic login working
- **Full**: User needs custom fields, TypeScript types, or all user data

**Create the Quick Setup Version for most users:**

```typescript
create_file(
  path: "/home/claude/auth.ts",
  file_text: `import NextAuth from "next-auth";

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    {
      id: "codebasics",
      name: "Codebasics",
      type: "oauth",
      authorization: {
        url: "https://codebasics.io/oauth/authorize",
        params: { scope: "read-user" },
      },
      token: "https://codebasics.io/oauth/token",
      userinfo: "https://codebasics.io/api/user",
      clientId: process.env.AUTH_CODEBASICS_ID!,
      clientSecret: process.env.AUTH_CODEBASICS_SECRET!,
      profile(profile) {
        return {
          id: profile.id.toString(),
          name: profile.full_name,
          email: profile.email,
          image: profile.avatar,
        };
      },
    },
  ],
  callbacks: {
    async jwt({ token, account }) {
      if (account) token.accessToken = account.access_token;
      return token;
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken as string;
      return session;
    },
  },
});
`
)
```

**Create the Full-Featured Version when users need custom fields:**

```typescript
create_file(
  path: "/home/claude/auth.ts",
  file_text: `import NextAuth from "next-auth";

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    {
      id: "codebasics",
      name: "Codebasics",
      type: "oauth",
      authorization: {
        url: \`\${process.env.CODEBASICS_BASE_URL}/oauth/authorize\`,
        params: {
          scope: "read-user",
          response_type: "code",
        },
      },
      token: \`\${process.env.CODEBASICS_BASE_URL}/oauth/token\`,
      userinfo: \`\${process.env.CODEBASICS_BASE_URL}/api/user\`,
      clientId: process.env.AUTH_CODEBASICS_ID!,
      clientSecret: process.env.AUTH_CODEBASICS_SECRET!,
      profile(profile) {
        return {
          id: profile.id.toString(),
          name: profile.name || profile.full_name,
          email: profile.email,
          image: profile.avatar,
          // Custom fields
          emailVerified: profile.email_verified,
          role: profile.role_name,
          mobile: profile.mobile,
          bio: profile.bio,
          headline: profile.headline,
          location: profile.location,
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
        token.profile = profile;
      }
      return token;
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken as string;
      session.user = {
        ...session.user,
        ...token.profile,
      };
      return session;
    },
  },
  debug: process.env.NODE_ENV === "development",
});
`
)
```

**After creating:** Tell user this file goes in the project root.

#### File 3: API Route Handler

**Create the route handler file:**

```typescript
create_file(
  path: "/home/claude/route.ts",
  file_text: `import { handlers } from "@/auth";
export const { GET, POST } = handlers;
`
)
```

**After creating:** Tell user this file goes in `app/api/auth/[...nextauth]/route.ts`
- They may need to create the directory structure: `app/api/auth/[...nextauth]/`
- The `[...nextauth]` folder name is important (it's a catch-all route)

#### File 4: TypeScript Types (for TypeScript projects)

**Create the type definition file:**

```typescript
create_file(
  path: "/home/claude/next-auth.d.ts",
  file_text: `import { DefaultSession } from "next-auth";

declare module "next-auth" {
  interface Session {
    accessToken?: string;
    user: {
      id: string;
      role?: string;
      mobile?: string;
      bio?: string;
      headline?: string;
      location?: string;
      emailVerified?: boolean;
    } & DefaultSession["user"];
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    accessToken?: string;
    refreshToken?: string;
    expiresAt?: number;
    profile?: any;
  }
}
`
)
```

**After creating:** Tell user this file goes in `types/next-auth.d.ts`
- They may need to create the `types/` directory
- This enables TypeScript autocomplete for custom session fields

### File Creation Workflow

**Always follow this workflow when helping users:**

1. **Ask Questions First**
   - Understand what they need (quick setup vs full setup)
   - Check if they have OAuth credentials
   - Confirm TypeScript vs JavaScript
   - Understand their project structure

2. **Create All Necessary Files**
   - Use `create_file` for each file
   - Create files in `/home/claude/` first
   - Name files clearly (e.g., `auth.ts`, `.env.local`, `route.ts`, `next-auth.d.ts`)

3. **Move Files to Outputs**
   - Copy all created files to `/mnt/user-data/outputs/` so user can download them
   - Use `bash_tool` to copy: `cp /home/claude/*.ts /mnt/user-data/outputs/`

4. **Present Files to User**
   - Use `present_files` tool to share all created files
   - Provide clear instructions on where each file should go in their project

5. **Give Next Steps**
   - Installation commands (`npm install next-auth@beta`)
   - Commands to run (`openssl rand -base64 32` for AUTH_SECRET)
   - Directory structure they need to create
   - Testing checklist

**Example Complete Workflow:**

```
User: "I want to add Login with Codebasics to my Next.js app"

Claude Actions:
1. Ask: "Do you have your Client ID and Secret? Are you using TypeScript?"
2. Create: .env.local, auth.ts, route.ts, next-auth.d.ts (if TypeScript)
3. Move: cp /home/claude/* /mnt/user-data/outputs/
4. Present: present_files([".env.local", "auth.ts", "route.ts", "next-auth.d.ts"])
5. Instruct: "Here are your files. Place them as follows:
   - .env.local → project root
   - auth.ts → project root  
   - route.ts → app/api/auth/[...nextauth]/route.ts
   - next-auth.d.ts → types/next-auth.d.ts"
```

### File Organization Guide

After creating files, tell users exactly where to place them:

| Created File | User's Project Location | Notes |
|-------------|------------------------|-------|
| `.env.local` | `project-root/.env.local` | Never commit to git |
| `auth.ts` | `project-root/auth.ts` | Must be in root, not app/ |
| `route.ts` | `app/api/auth/[...nextauth]/route.ts` | Create directories if needed |
| `next-auth.d.ts` | `types/next-auth.d.ts` | TypeScript only |
| `page.tsx` (login) | `app/login/page.tsx` or `app/page.tsx` | User choice |

### Step 3: Provide Implementation Examples

**Create actual example files when users need them.**

#### Login Page Example

**When user needs a login page, create it:**

```typescript
create_file(
  path: "/home/claude/page.tsx",
  file_text: `import { signIn, auth } from "@/auth";

export default async function LoginPage() {
  const session = await auth();

  if (session) {
    return (
      <div>
        <h1>Welcome, {session.user?.name}!</h1>
        <p>Email: {session.user?.email}</p>
        <form
          action={async () => {
            "use server";
            await signOut();
          }}
        >
          <button type="submit">Sign out</button>
        </form>
      </div>
    );
  }

  return (
    <div>
      <h1>Login</h1>
      <form
        action={async () => {
          "use server";
          await signIn("codebasics");
        }}
      >
        <button type="submit">Sign in with Codebasics</button>
      </form>
    </div>
  );
}
`
)
```

**After creating:** Tell user this can go in `app/page.tsx` or `app/login/page.tsx`

#### Client-Side Usage (when needed)

**If user needs client-side components, create them:**

```typescript
create_file(
  path: "/home/claude/LoginButton.tsx",
  file_text: `"use client";

import { useSession, signIn, signOut } from "next-auth/react";

export function LoginButton() {
  const { data: session } = useSession();

  if (session) {
    return (
      <div>
        <p>Signed in as {session.user?.email}</p>
        <button onClick={() => signOut()}>Sign out</button>
      </div>
    );
  }

  return <button onClick={() => signIn("codebasics")}>Sign in with Codebasics</button>;
}
`
)
```

**After creating:** Tell user:
- This can go in `components/LoginButton.tsx`
- They need to wrap their app with `<SessionProvider>` for client components to work

**Create the SessionProvider wrapper if needed:**

```typescript
create_file(
  path: "/home/claude/layout.tsx",
  file_text: `import { SessionProvider } from "next-auth/react";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <SessionProvider>{children}</SessionProvider>
      </body>
    </html>
  );
}
`
)
```

**After creating:** Tell user this replaces their `app/layout.tsx`

#### Making API Calls with Access Token

**When user needs examples of API calls, create actual files:**

**Server Component Example:**

```typescript
create_file(
  path: "/home/claude/ProfilePage.tsx",
  file_text: `import { auth } from "@/auth";

export default async function ProfilePage() {
  const session = await auth();
  
  if (!session?.accessToken) {
    return <div>Please log in to view your profile</div>;
  }

  try {
    const response = await fetch(
      \`\${process.env.CODEBASICS_BASE_URL}/api/user\`,
      {
        headers: {
          Authorization: \`Bearer \${session.accessToken}\`,
        },
      }
    );

    if (!response.ok) {
      throw new Error("Failed to fetch user data");
    }

    const userData = await response.json();
    
    return (
      <div>
        <h1>Profile</h1>
        <p>Name: {userData.full_name}</p>
        <p>Email: {userData.email}</p>
        <p>Role: {userData.role_name}</p>
        {userData.bio && <p>Bio: {userData.bio}</p>}
        {userData.headline && <p>Headline: {userData.headline}</p>}
      </div>
    );
  } catch (error) {
    return <div>Error loading profile: {error.message}</div>;
  }
}
`
)
```

**After creating:** Tell user this can go in `app/profile/page.tsx`

**API Route Example:**

```typescript
create_file(
  path: "/home/claude/user-route.ts",
  file_text: `import { auth } from "@/auth";
import { NextResponse } from "next/server";

export async function GET() {
  const session = await auth();
  
  if (!session?.accessToken) {
    return NextResponse.json(
      { error: "Unauthorized" }, 
      { status: 401 }
    );
  }

  try {
    const response = await fetch(
      \`\${process.env.CODEBASICS_BASE_URL}/api/user\`,
      {
        headers: {
          Authorization: \`Bearer \${session.accessToken}\`,
        },
      }
    );

    if (!response.ok) {
      throw new Error("Failed to fetch user data");
    }

    const userData = await response.json();
    return NextResponse.json(userData);
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to fetch user data" },
      { status: 500 }
    );
  }
}
`
)
```

**After creating:** Tell user this goes in `app/api/user/route.ts`

### Step 4: Troubleshooting Guide

When users encounter issues, help them diagnose and fix:

#### Common Issues and Solutions

**1. Redirect URI Mismatch**
- Error: `invalid_request: The redirect URI is invalid`
- Solution: 
  - Verify redirect URL in OAuth client matches exactly: `http://localhost:3000/api/auth/callback/codebasics`
  - Check for trailing slashes
  - Ensure provider `id` in config matches the callback URL path

**2. Invalid Client**
- Error: `invalid_client`
- Solution:
  - Verify `AUTH_CODEBASICS_ID` and `AUTH_CODEBASICS_SECRET` are correct
  - Ensure credentials are not expired
  - Check OAuth client is active in developer portal

**3. Token Expired**
- Error: `token_expired` or `401 Unauthorized`
- Solution:
  - Access tokens expire after 15 days
  - Implement token refresh logic or prompt re-authentication
  - Check token expiry: `session.expiresAt`

**4. Session is Null**
- Solution:
  - Ensure `auth.ts` is in project root, not in `app/` folder
  - Wrap client components with `<SessionProvider>`
  - Check that environment variables are loaded

**5. CORS Errors**
- Solution:
  - OAuth flow uses server-side redirects (no CORS issues)
  - If making direct API calls, contact Codebasics support

**6. Scope Issues**
- Error: `invalid_scope`
- Solution: Use scope `read-user` only

## Installation Steps

When guiding users through initial setup:

1. **Install Dependencies**
   ```bash
   npm install next-auth@beta
   ```

2. **Create OAuth Credentials**
   - Navigate to: https://codebasics.io/panel/developer/oauth-clients
   - Click "Create New Client"
   - Fill in application name
   - Set redirect URL: `http://localhost:3000/api/auth/callback/codebasics`
   - Save Client ID and Client Secret

3. **Generate Auth Secret**
   ```bash
   openssl rand -base64 32
   ```

4. **Create Configuration Files**
   - `.env.local` with environment variables
   - `auth.ts` in project root
   - `app/api/auth/[...nextauth]/route.ts`
   - `types/next-auth.d.ts` (if TypeScript)

5. **Test the Integration**
   - Run `npm run dev`
   - Navigate to login page
   - Click "Sign in with Codebasics"
   - Should redirect to Codebasics login
   - After login, redirect back with session

## Best Practices to Emphasize

1. **Security:**
   - Never commit secrets to version control
   - Use HTTPS in production
   - Validate redirect URIs
   - Rotate secrets periodically
   - Create separate OAuth clients for dev/staging/prod

2. **Error Handling:**
   - Implement proper error pages
   - Handle token expiry gracefully
   - Log authentication errors in development

3. **User Experience:**
   - Show loading states during redirect
   - Provide clear error messages
   - Handle edge cases (network failures, etc.)

## User Data Structure

The `/api/user` endpoint returns:

```typescript
interface CodebasicsUser {
  // Basic Information
  id: number;
  name: string;
  full_name: string;
  email: string;
  email_verified: boolean;
  verified: boolean;

  // Profile Details
  role_name: string;
  organ_id: number | null;
  mobile: string | null;
  gender: string | null;
  dob: string | null;
  bio: string | null;
  headline: string | null;
  about: string | null;

  // Social
  discord_id: string | null;

  // Permissions
  financial_approval: boolean;
  status: string;
  access_content: number;

  // Media
  avatar: string | null;
  avatar_settings: object | null;
  cover_img: string | null;

  // Location
  address: string | null;
  country_id: number | null;
  province_id: number | null;
  city_id: number | null;
  district_id: number | null;
  location: string | null;

  // Training/Meeting
  level_of_training: string | null;
  meeting_type: string | null;

  // Purchases
  purchased_items: any[];
}
```

## Response Strategy

### PRIMARY RULE: CREATE FILES, DON'T JUST SHOW CODE

**This skill MUST create actual files using `create_file` tool.** Users expect downloadable files, not code snippets to copy-paste.

### When User Asks for Quick Setup

1. **Ask essential questions** (have credentials? TypeScript? project structure?)
2. **Create all necessary files** using `create_file`:
   - `.env.local`
   - `auth.ts`
   - `route.ts` (for API route handler)
   - `next-auth.d.ts` (if TypeScript)
   - `page.tsx` (login page example)
3. **Move files to outputs** using `bash_tool`
4. **Present files** using `present_files` tool
5. **Provide clear instructions** on where to place each file
6. **List next steps** (install commands, generate secrets, test)

**Example Response Flow:**

```
User: "I want to add Login with Codebasics to my Next.js app"

Claude:
1. "Great! Do you have your Client ID and Secret from Codebasics? Are you using TypeScript?"
   [User responds]

2. [Creates files using create_file]
   - create_file(.env.local)
   - create_file(auth.ts)
   - create_file(route.ts)
   - create_file(next-auth.d.ts)
   - create_file(page.tsx)

3. [Moves to outputs]
   bash_tool: cp /home/claude/* /mnt/user-data/outputs/

4. [Presents files]
   present_files([.env.local, auth.ts, route.ts, next-auth.d.ts, page.tsx])

5. "Here are all your files! Place them as follows:
   - .env.local → project root
   - auth.ts → project root
   - route.ts → app/api/auth/[...nextauth]/route.ts
   - next-auth.d.ts → types/next-auth.d.ts
   - page.tsx → app/login/page.tsx (or app/page.tsx)
   
   Next steps:
   1. Run: npm install next-auth@beta
   2. Generate AUTH_SECRET: openssl rand -base64 32
   3. Update .env.local with your credentials
   4. Test: npm run dev"
```

### When User Has Specific Issues
1. Confirm they have OAuth credentials
2. Generate all necessary files in one response
3. Provide clear next steps
4. Offer to help with specific customizations

### When User Has Specific Issues

1. **Ask diagnostic questions** to understand the error
2. **Identify the root cause** from error messages
3. **If they need a corrected file**, create it using `create_file`
4. **Explain what was wrong** and what you fixed
5. **Present the corrected file** using `present_files`
6. **Verify the fix** (ask if it worked)

**Example:**

```
User: "Getting redirect URI mismatch error"

Claude:
1. "Can you share your auth.ts file? What's the provider id you're using?"
2. [Identifies issue: provider id is "codebasics-oauth" instead of "codebasics"]
3. [Creates corrected auth.ts file]
4. "The issue is your provider id. It should be 'codebasics' not 'codebasics-oauth'. 
   The provider id determines the callback URL path. Here's the corrected file."
5. [Presents corrected auth.ts]
```

### When User Wants Customization

1. **Understand what they want** (custom fields, styling, etc.)
2. **Create modified files** with their customizations
3. **Explain the changes** you made
4. **Present the files** using `present_files`
5. **Highlight security considerations** if applicable

**Example:**

```
User: "I want to add the user's role and bio to the session"

Claude:
1. [Creates updated auth.ts with role and bio in profile()]
2. [Creates updated next-auth.d.ts with role and bio types]
3. "I've updated two files:
   - auth.ts: Added role and bio to the profile mapping
   - next-auth.d.ts: Added TypeScript types for these fields
   
   Now you can access session.user.role and session.user.bio"
4. [Presents both files]
```

### General Guidelines

- **Always create files** - Don't just show code blocks
- **Be complete** - Include all necessary files for the task
- **Be clear** - Explain where each file goes
- **Be secure** - Remind about secrets, .gitignore, HTTPS
- **Be helpful** - Provide next steps and testing guidance
- **Use present_files** - Always deliver files to user

## File Organization

Always create files in the correct locations:
- `auth.ts` → Project root
- `.env.local` → Project root
- `app/api/auth/[...nextauth]/route.ts` → App directory
- `types/next-auth.d.ts` → Types directory (create if needed)
- Login pages → `app/login/page.tsx` or `app/page.tsx`

## Additional Resources to Reference

- Auth.js Documentation: https://authjs.dev
- OAuth Client Portal: https://codebasics.io/panel/developer/oauth-clients
- Next.js App Router: https://nextjs.org/docs/app

## Key Reminders

1. **CREATE FILES, DON'T JUST SHOW CODE** - Use `create_file` tool for every file
2. **MOVE FILES TO OUTPUTS** - Use `bash_tool` to copy to `/mnt/user-data/outputs/`
3. **PRESENT FILES TO USER** - Use `present_files` tool to deliver files
4. **Always use App Router** - This skill focuses on Next.js App Router, not Pages Router
5. **Provider ID must be "codebasics"** - This determines the callback URL
6. **Scope is always "read-user"** - Don't use other scopes
7. **Direct redirect flow** - No separate login form; clicking button redirects to Codebasics
8. **Access token in session** - Store via callbacks for API calls
9. **15-day token expiry** - Remind users to handle token refresh
10. **File locations matter**:
    - `auth.ts` → project root (NOT in app/ directory)
    - `.env.local` → project root
    - Route handler → `app/api/auth/[...nextauth]/route.ts`
    - Types → `types/next-auth.d.ts`

## Tone and Communication

- Be helpful and encouraging
- Provide complete, working code
- Explain "why" not just "what"
- Anticipate common mistakes
- Use clear, jargon-free language when possible
- If user seems inexperienced, explain concepts briefly
- If user is experienced, be concise

## Testing Checklist

Help users verify their setup:
- [ ] Environment variables set correctly
- [ ] OAuth redirect URI matches exactly
- [ ] Can redirect to Codebasics login
- [ ] Can authenticate successfully
- [ ] Redirected back after login
- [ ] Session contains user data and accessToken
- [ ] Can make API calls with accessToken
- [ ] Sign out works correctly