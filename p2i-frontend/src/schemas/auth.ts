import z from "zod";

export const signupSchema = z.object({
    email: z.string().email("Please enter a valid email"),
    password: z.string().min(8,"password must be at least 8 charchters"),

})

export const loginSchema = z.object({
    email: z.string().email("Please enter a valid email"),
    password: z.string().min(1,"password is required"),

})

export type LoginFormValues = z.infer<typeof loginSchema>;
export type SignupFormValues = z.infer<typeof signupSchema>;