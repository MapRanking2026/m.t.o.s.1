import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Chrome } from "lucide-react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { supabase } from "@/lib/supabase";

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleGoogleLogin = async () => {
    setIsSubmitting(true);
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: `${window.location.origin}/`,
        },
      });
      if (error) {
        toast.error(error.message);
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Google login failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    try {
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) {
        toast.error(error.message);
        return;
      }
      toast.success("Signed in");
      navigate("/", { replace: true });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Login failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = async () => {
    if (!email) {
      toast.error("Enter your email first");
      return;
    }
    setIsSubmitting(true);
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email);
      if (error) {
        toast.error(error.message);
        return;
      }
      toast.success("Password reset email sent");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Reset failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-6xl items-center justify-center px-6 py-10">
      <Card className="w-full max-w-lg p-8">
        <Badge>MTOS Login</Badge>
        <h1 className="mt-5 font-display text-4xl text-white">Sign in</h1>
        <p className="mt-3 text-sm text-muted-foreground">
          Use your agency email. Access is enforced by your tenant membership and role.
        </p>

        <div className="mt-8 space-y-3">
          <Button className="w-full justify-center" disabled={isSubmitting} onClick={handleGoogleLogin} type="button" variant="secondary">
            <Chrome className="h-4 w-4" />
            Continue with Google
          </Button>
        </div>

        <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
          <label className="block space-y-2">
            <span className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Email</span>
            <input
              className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none ring-0 transition focus:border-emerald-300/40 focus:bg-white/[0.06]"
              autoComplete="email"
              inputMode="email"
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@agency.com"
              required
              type="email"
              value={email}
            />
          </label>

          <label className="block space-y-2">
            <span className="text-xs uppercase tracking-[0.18em] text-muted-foreground">Password</span>
            <input
              className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none ring-0 transition focus:border-emerald-300/40 focus:bg-white/[0.06]"
              autoComplete="current-password"
              onChange={(event) => setPassword(event.target.value)}
              required
              type="password"
              value={password}
            />
          </label>

          <div className="flex flex-col gap-3 pt-2 sm:flex-row sm:items-center sm:justify-between">
            <Button className="sm:w-auto" disabled={isSubmitting} type="submit">
              {isSubmitting ? "Signing in..." : "Sign in"}
            </Button>
            <button
              className="text-sm text-muted-foreground transition hover:text-white"
              disabled={isSubmitting}
              onClick={handleReset}
              type="button"
            >
              Forgot password?
            </button>
          </div>
        </form>
      </Card>
    </div>
  );
}
