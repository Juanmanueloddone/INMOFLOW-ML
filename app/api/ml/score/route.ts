import { NextResponse } from "next/server";

const USE_ML = (process.env.USE_ML || "false").toLowerCase() === "true";

export async function POST(req: Request) {
  const { demanda_id, propiedad_id } = await req.json();

  if (!USE_ML) {
    return NextResponse.json({
      demanda_id, propiedad_id,
      score_ml: null, rank_ml: null,
      model_version: "none", features_used_hash: null,
    });
  }

  // (Futuro: si USE_ML=true, leer de match_model_scores en Supabase y devolverlo)
  return NextResponse.json({
    demanda_id, propiedad_id,
    score_ml: null, rank_ml: null,
    model_version: "pending", features_used_hash: null,
  });
}
