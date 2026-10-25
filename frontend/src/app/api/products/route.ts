
import { NextResponse } from "next/server";

export async function GET() {
  const apiBaseUrl =
    process.env.BACKEND_URL ?? "http://127.0.0.1:8010";

  try {
    const response = await fetch(`${apiBaseUrl}/products`, {
      cache: "no-store",
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: "Не удалось загрузить каталог товаров" },
        { status: 502 },
      );
    }

    const products: unknown = await response.json();

    if (!Array.isArray(products)) {
      return NextResponse.json(
        { error: "Сервер вернул некорректный список товаров" },
        { status: 502 },
      );
    }

    return NextResponse.json(products, {
      headers: { "Cache-Control": "no-store" },
    });
  } catch {
    return NextResponse.json(
      { error: "Сервер временно недоступен" },
      { status: 502 },
    );
  }
}
