
"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import styles from "./page.module.css";

type Product = {
  id: number;
  title: string;
};

export default function Home() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function loadProducts() {
      try {
        const response = await fetch("/api/products", {
          signal: controller.signal,
          cache: "no-store",
        });

        if (!response.ok) {
          throw new Error("Не удалось загрузить каталог");
        }

        const data: unknown = await response.json();

        if (
          !Array.isArray(data) ||
          !data.every(
            (item): item is Product =>
              typeof item.id === "number" &&
              typeof item.title === "string",
          )
        ) {
          throw new Error("Получен некорректный список товаров");
        }

        setProducts(data);
      } catch (err) {
        if (controller.signal.aborted) return;

        setError(
          err instanceof Error
            ? err.message
            : "Не удалось загрузить каталог",
        );
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    void loadProducts();

    return () => controller.abort();
  }, []);

  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <Link className={styles.brand} href="/">
          <span className={styles.brandMark} aria-hidden="true">
            К
          </span>
          <span>Каталог</span>
        </Link>
        <span className={styles.headerLabel}>Коллекция товаров</span>
      </header>

      <section className={styles.hero}>
        <p className={styles.eyebrow}>НАША КОЛЛЕКЦИЯ</p>
        <h1>Товары</h1>
        <p className={styles.subtitle}>
          Всё, что есть в каталоге, — в одном месте.
        </p>
      </section>

      <section className={styles.catalog} aria-label="Каталог товаров">
        <div className={styles.catalogHeading}>
          <h2>Весь каталог</h2>
          {!loading && !error && (
            <span className={styles.count}>
              {products.length}{" "}
              {products.length === 1
                ? "товар"
                : products.length >= 2 &&
                    products.length <= 4
                  ? "товара"
                  : "товаров"}
            </span>
          )}
        </div>

        {loading && (
          <p className={styles.message} role="status">
            Загружаем каталог…
          </p>
        )}

        {error && (
          <div className={styles.message} role="alert">
            <p>{error}</p>
            <button
              className={styles.retryButton}
              onClick={() => window.location.reload()}
            >
              Попробовать снова
            </button>
          </div>
        )}

        {!loading && !error && products.length === 0 && (
          <p className={styles.message}>
            Пока товаров нет. Загляните позже.
          </p>
        )}

        {!loading && !error && products.length > 0 && (
          <div className={styles.grid}>
            {products.map((product) => (
              <article className={styles.card} key={product.id}>
                <div className={styles.imageFrame}>
                  <img
                    className={styles.productImage}
                    src={`/api/products/${product.id}/image`}
                    alt={product.title}
                    loading="lazy"
                    onError={(event) => {
                      const image = event.currentTarget;
                      image.style.display = "none";
                      image.parentElement?.classList.add(
                        styles.noImage,
                      );
                    }}
                  />
                  <span className={styles.imagePlaceholder}>
                    <span aria-hidden="true">◇</span>
                    <span>Фото отсутствует</span>
                  </span>
                </div>

                <div className={styles.cardBody}>
                  <span className={styles.productNumber}>
                    ТОВАР № {product.id}
                  </span>
                  <h3 className={styles.productTitle}>
                    {product.title}
                  </h3>
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      <footer className={styles.footer}>
        Каталог товаров
      </footer>
    </main>
  );
}
