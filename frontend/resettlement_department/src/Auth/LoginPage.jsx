import AuthImage from "./AuthImage";
import LoginForm from "./LoginForm";

const LoginPage = () => {
    return (
      <div className="w-full lg:grid lg:min-h-screen bg-gray-200 text-black lg:grid-cols-2 xl:min-h-screen">
              <div class="block1 z-10 flex min-h-screen items-center justify-center py-12 shadow-2xl">
                  <div class="mx-auto grid w-[350px] gap-6">
                      <div class="grid gap-2 text-center">
                          <h1 class="text-3xl font-bold">Добро пожаловать</h1>
                          <p class="text-grey text-muted-foreground pb-4">Введите данные для входа</p>
                          <LoginForm />
                      </div>
                  </div>
              </div>
              <div class="block2 hidden overflow-hidden bg-gradient-to-br from-slate-200 via-gray-50 to-stone-200 lg:block">
                  <AuthImage/>
              </div>
          </div>
    );
  };
  
  export default LoginPage;