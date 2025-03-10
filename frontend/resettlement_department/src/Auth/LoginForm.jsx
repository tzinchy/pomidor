import { useForm } from "react-hook-form";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import Cookies from "js-cookie";
import { Eye, EyeOff } from "lucide-react";



const LoginForm = () => {
  const { register, handleSubmit, formState: { errors } } = useForm();
  const navigate = useNavigate();
  const [message, setMessage] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  

  const onSubmit = async (data) => {
    try {
      const formData = new URLSearchParams();
      
      formData.append("email", data.email);
      formData.append("password", data.password);

      const response = await axios.post(`http://10.9.96.160/api/login/auth/auth/login`, data, {
        headers: { "Content-Type": "application/json" }, withCredentials:  "include",
      });

      localStorage.setItem("token", response.data.access_token);
    //   Cookies.set("access_token", response.data.access_token, {
    //     expires: 180, // Срок действия 7 дней
    //     path: "/", // Кука будет доступна на всем сайте
    //     // secure: true, // Только через HTTPS
    //     sameSite: "Strict", // Защита от CSRF
    //   });
      setMessage("Успешный вход!");
      navigate("/dashboard");  // Перенаправляем на домашнюю страницу
      // window.location.href = "http://10.9.96.160:3001/dashboard"

    } catch (error) {
      setMessage("❌ Ошибка: " + (error.response?.data?.detail || "Неизвестная ошибка"));
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
          
            <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-left m-6">Логин или EMAIL</label>
            <input 
              {...register("email", { required: "❌ Адрес электронной почты обязателен",
                // pattern: {
                //   value: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
                //   message: "❌ Введите корректный email"
                // }
               })} 
              type="text" 
              className="border border-gray-300 bg-transparent ring-offset-background placeholder:text-muted-foreground focus-visible:ring-ring flex h-10 w-full rounded-md px-3 py-2 text-sm file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:cursor-not-allowed disabled:opacity-70" id="email" name="email" aria-describedby=":r1:-form-item-description" aria-invalid="false"
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
        className="peer border border-gray-300 bg-transparent ring-offset-background 
                   placeholder:text-muted-foreground focus-visible:ring-ring 
                   flex h-10 w-full rounded-md px-3 py-2 pr-10 text-sm 
                   file:border-0 file:bg-transparent file:text-sm file:font-medium 
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