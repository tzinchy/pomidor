import { useForm } from "react-hook-form";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import Cookies from "js-cookie";
const backendUrl = import.meta.env.VITE_BACKEND_URL;
import { Eye, EyeOff } from "lucide-react";

const LoginForm = ( {redirectUri} ) => {
  const { register, handleSubmit, formState: { errors } } = useForm();
  const navigate = useNavigate();
  const [message, setMessage] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  

  const onSubmit = async (data) => {
    try {
      // const formData = new URLSearchParams();
      data.login_or_email = data.login_or_email.toLowerCase()
      // formData.append("login_or_email", data.login_or_email.toLowerCase());
      // formData.append("password", data.password);

      const response = await axios.post(`${backendUrl}/v1/auth/login`, data, {
        headers: { "Content-Type": "application/json" }, withCredentials:  "include",
      });

        Cookies.set("roles", response.data.user.roles, {
          expires: 180, // Срок действия 7 дней
          path: "/", // Кука будет доступна на всем сайте
          secure: true, // Только через HTTPS
          sameSite: "None", // Защита от CSRF
          domain: import.meta.env.VITE_DOMAIN_ZONE,
        });

    //   Cookies.set("access_token", response.data.access_token, {
    //     expires: 180, // Срок действия 7 дней
    //     path: "/", // Кука будет доступна на всем сайте
    //     // secure: true, // Только через HTTPS
    //     sameSite: "Strict", // Защита от CSRF
    //   });
      setMessage("Успешный вход!");
      // navigate("/home");  // Перенаправляем на домашнюю страницу
      window.location.href = redirectUri
      // alert("Успех, проверяй куки")

    } catch (error) {
      setMessage("❌ Ошибка: " + (error.response?.data?.detail || error));
    }
  };

  return (
    // <div class="block1 z-10 flex min-h-screen items-center justify-center py-12 shadow-2xl">
    //     <div class="mx-auto grid w-[350px] gap-6">
    //         <div class="grid gap-2 text-center">
    //             <h1 class="text-3xl font-bold">Добро пожаловать</h1>
    //     {message && <p className="text-center text-red-500">{message}</p>}
        <form onSubmit={handleSubmit(onSubmit)} class="grid gap-5 text-center">
          {message && <p className="mt-3 text-center text-red font-semibold">{message}</p>}
          <div>
          
            <label className="text-sm font-medium  leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-left m-6">Логин или EMAIL</label>
            <input 
              {...register("login_or_email", { required: "❌ Адрес электронной почты обязателен",
                // pattern: {
                //   value: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
                //   message: "❌ Введите корректный email"
                // }
               })} 
              type="text" 
              
              className="border-input text-transform: lowercase; bg-transparent ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring flex h-10 w-full rounded-md border px-3 py-2 text-sm file:border-0 file:bg-transparent file:text-sm file:font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-70" id="login_or_email" name="login_or_email" aria-describedby=":r1:-form-item-description" aria-invalid="false"
            //   placeholder="Введите логин"
            />
            
            {errors.email && <p className="text-red-500 mt-2 text-sm">{errors.email.message}</p>}
          </div>
          <div>
            <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-left">Пароль</label>
            <div className="relative w-full">
      <input
        {...register("password", { required: "❌ Пароль обязателен" })}
        type={showPassword ? "text" : "password"}
        className="peer border-input bg-transparent ring-offset-background 
                   placeholder:text-muted-foreground focus-visible:ring-ring 
                   flex h-10 w-full rounded-md border px-3 py-2 pr-10 text-sm 
                   file:border-0 file:bg-transparent file:text-sm file:font-medium 
                   focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 
                   disabled:cursor-not-allowed disabled:opacity-50"
        id="password"
        name="password"
        aria-describedby="password-description"
        aria-invalid="false"
      />
      <button
        onClick={() => setShowPassword(!showPassword)}
        type="button"
        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
      >
        {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
      </button>
    </div>
            {errors.password && <p className="text-red-500 mt-2 text-sm">{errors.password.message}</p>}
          </div>
          <button 
            type="submit" 
            className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border-transparent bg-black text-white hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2 w-full"
                     >
            Войти
          </button>
          <a href="/register">
          {/* <button type="button" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2 w-full">
            Регистрация
          </button> */}
          
          </a>
        </form>
    //   </div>
    // </div>
    // </div>
  );
};

export default LoginForm;