
import React from "react";
import {Home}  from "lucide-react"

export function TopBar() {
  return (
    <div className="flex items-center justify-start gap-4 pl-24 py-4 bg-white shadow-md ">
    <a className="flex items-center justify-center rounded-full shadow-sm bg-gray-200 p-2 w-16 h-16" href="/">
        <Home size={30} className="text-gray-700" />
    </a>
    <div className="text-3xl font-bold">AI 정리 정돈 도우미</div>
    </div>
  );
}