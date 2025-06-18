"use client";

import { cn } from "~/lib/utils";

import Link from "next/link";
import { signIn } from "next-auth/react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Button } from "./ui/button";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { loginSchema, signupSchema, type LoginFormValues, type SignupFormValues } from "~/schemas/auth";
import { signUp } from "~/actions/auth";
import { useRouter } from "next/navigation";


export function LoginForm({
  className,
  ...props
}: React.ComponentPropsWithoutRef<"div">) {

    const [error, setError] = useState<string | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const router = useRouter();

    const {register, handleSubmit, formState:{errors}}= useForm<LoginFormValues>({resolver: zodResolver(loginSchema)})

    const onSubmit = async(data: LoginFormValues) => {
        try {
      setIsSubmitting(true);
      setError(null);

      // const result = await signUp(data);
      // if (!result.success) {
      //   setError(result.error ?? "An error occured during signup");
      //   return;
      // }

      const signInResult = await signIn("credentials", {
        email: data.email,
        password: data.password,
        redirect: false,
      });

      if (signInResult?.error) {
        setError(
          "Invalid email or password",
        );
      } else {
        router.push("/dashboard");
      }
    } catch (error) {
      setError("An unexpected error occured");
    } finally {
      setIsSubmitting(false);
    }

    }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">LogIn</CardTitle>
          <CardDescription>
            Enter your email below to login to your account
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="flex flex-col gap-6">
              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="m@example.com"
                  required
                  {...register("email")}
                />
                {errors.email && (<p className="text-sm text-red-500">{"errors.email.message"}</p>)}
              </div>
              <div className="grid gap-2">
                <div className="flex items-center">
                  <Label htmlFor="password">Password</Label>
                  <a
                    href="#"
                    className="ml-auto inline-block text-sm underline-offset-4 hover:underline"
                  >
                    Forgot your password?
                  </a>
                </div>
                <Input id="password" type="password" required {...register("password")} />
                {errors.password && (<p className="text-sm text-red-500">{"errors.password.message"}</p>)}
              </div>

              {error && (<p className="text-red-500 rounded-md bg-red-50 text-sm p-3">{"error"}</p>)}
              <Button type="submit" className="w-full" disabled={isSubmitting}>
                {isSubmitting ? "Signing up..." : "Sign up"}
              </Button>
              
            </div>
            <div className="mt-4 text-center text-sm">
              Don't have an account?{" "}
              <Link href="/signup" className="underline underline-offset-4">
                Sign Up
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}