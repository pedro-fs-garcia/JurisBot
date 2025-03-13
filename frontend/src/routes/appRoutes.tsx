import { BrowserRouter, Route, Routes } from "react-router-dom";
import HomePage from "../pages/homePage";

export default function AppRoutes(){

    return(
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<HomePage/>} />
                {/* <Route path="/dashboard" element={<DashboardPage/>} /> */}
            </Routes>
        </BrowserRouter>
    );
}