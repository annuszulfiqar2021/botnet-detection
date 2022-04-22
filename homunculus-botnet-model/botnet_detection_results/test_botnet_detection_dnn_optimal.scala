package spatial.tests.feature.transfers

import argon.static.Sym
import spatial.dsl._

@spatial class test_botnet_detection_dnn_optimal extends SpatialTest {

	import spatial.lang.{AxiStream512, AxiStream512Bus}

	def main(args: Array[String]): Unit = {

		val N = 1
		val project_dir = s"botnet_detection_results/luts"

		type T = FixPt[TRUE, _16, _16]

		val num_fields = 30

		val L0_Dim0 = 7
		val L0_Dim1 = 30

		val L1_Dim0 = 8
		val L1_Dim1 = 7

		val L2_Dim0 = 1
		val L2_Dim1 = 8

		val L3_Dim0 = 7
		val L3_Dim1 = 1

		val L4_Dim0 = 1
		val L4_Dim1 = 7

		val L5_Dim0 = 7
		val L5_Dim1 = 1

		val L6_Dim0 = 6
		val L6_Dim1 = 7

		val L7_Dim0 = 2
		val L7_Dim1 = 6

		val L8_Dim0 = 7
		val L8_Dim1 = 2

		val L9_Dim0 = 9
		val L9_Dim1 = 7

		val L10_Dim0 = 2
		val L10_Dim1 = 9

		val inbus = StreamIn[AxiStream512](AxiStream512Bus(tid = 0, tdest = 0))
		val outbus = StreamOut[AxiStream512](AxiStream512Bus(tid = 0, tdest = 1))

		Accel {

			val input = SRAM[T](num_fields)
			val packet_use1 = FIFO[AxiStream512](2)
			val packet_use2 = FIFO[AxiStream512](16)
			val dummy_stageinput_fifo = FIFO[T](2)
			val dummy_stage11_fifo = FIFO[I32](2)

			val dummy_stage0_fifo = FIFO[T](2)
			val L0_res = SRAM[T](L0_Dim0)
			val L0_W_LUT = LUT.fromFile[T](L0_Dim0 , L0_Dim1)(project_dir + "L0_NEURON_W_LUT.csv")
			val L0_B_LUT = LUT.fromFile[T](L0_Dim0)(project_dir + "L0_NEURON_B_LUT.csv")

			val dummy_stage1_fifo = FIFO[T](2)
			val L1_res = SRAM[T](L1_Dim0)
			val L1_W_LUT = LUT.fromFile[T](L1_Dim0 , L1_Dim1)(project_dir + "L1_NEURON_W_LUT.csv")
			val L1_B_LUT = LUT.fromFile[T](L1_Dim0)(project_dir + "L1_NEURON_B_LUT.csv")

			val dummy_stage2_fifo = FIFO[T](2)
			val L2_res = SRAM[T](L2_Dim0)
			val L2_W_LUT = LUT.fromFile[T](L2_Dim0 , L2_Dim1)(project_dir + "L2_NEURON_W_LUT.csv")
			val L2_B_LUT = LUT.fromFile[T](L2_Dim0)(project_dir + "L2_NEURON_B_LUT.csv")

			val dummy_stage3_fifo = FIFO[T](2)
			val L3_res = SRAM[T](L3_Dim0)
			val L3_W_LUT = LUT.fromFile[T](L3_Dim0 , L3_Dim1)(project_dir + "L3_NEURON_W_LUT.csv")
			val L3_B_LUT = LUT.fromFile[T](L3_Dim0)(project_dir + "L3_NEURON_B_LUT.csv")

			val dummy_stage4_fifo = FIFO[T](2)
			val L4_res = SRAM[T](L4_Dim0)
			val L4_W_LUT = LUT.fromFile[T](L4_Dim0 , L4_Dim1)(project_dir + "L4_NEURON_W_LUT.csv")
			val L4_B_LUT = LUT.fromFile[T](L4_Dim0)(project_dir + "L4_NEURON_B_LUT.csv")

			val dummy_stage5_fifo = FIFO[T](2)
			val L5_res = SRAM[T](L5_Dim0)
			val L5_W_LUT = LUT.fromFile[T](L5_Dim0 , L5_Dim1)(project_dir + "L5_NEURON_W_LUT.csv")
			val L5_B_LUT = LUT.fromFile[T](L5_Dim0)(project_dir + "L5_NEURON_B_LUT.csv")

			val dummy_stage6_fifo = FIFO[T](2)
			val L6_res = SRAM[T](L6_Dim0)
			val L6_W_LUT = LUT.fromFile[T](L6_Dim0 , L6_Dim1)(project_dir + "L6_NEURON_W_LUT.csv")
			val L6_B_LUT = LUT.fromFile[T](L6_Dim0)(project_dir + "L6_NEURON_B_LUT.csv")

			val dummy_stage7_fifo = FIFO[T](2)
			val L7_res = SRAM[T](L7_Dim0)
			val L7_W_LUT = LUT.fromFile[T](L7_Dim0 , L7_Dim1)(project_dir + "L7_NEURON_W_LUT.csv")
			val L7_B_LUT = LUT.fromFile[T](L7_Dim0)(project_dir + "L7_NEURON_B_LUT.csv")

			val dummy_stage8_fifo = FIFO[T](2)
			val L8_res = SRAM[T](L8_Dim0)
			val L8_W_LUT = LUT.fromFile[T](L8_Dim0 , L8_Dim1)(project_dir + "L8_NEURON_W_LUT.csv")
			val L8_B_LUT = LUT.fromFile[T](L8_Dim0)(project_dir + "L8_NEURON_B_LUT.csv")

			val dummy_stage9_fifo = FIFO[T](2)
			val L9_res = SRAM[T](L9_Dim0)
			val L9_W_LUT = LUT.fromFile[T](L9_Dim0 , L9_Dim1)(project_dir + "L9_NEURON_W_LUT.csv")
			val L9_B_LUT = LUT.fromFile[T](L9_Dim0)(project_dir + "L9_NEURON_B_LUT.csv")

			val dummy_stage10_fifo = FIFO[T](2)
			val L10_res = SRAM[T](L10_Dim0)
			val L10_W_LUT = LUT.fromFile[T](L10_Dim0 , L10_Dim1)(project_dir + "L10_NEURON_W_LUT.csv")
			val L10_B_LUT = LUT.fromFile[T](L10_Dim0)(project_dir + "L10_NEURON_B_LUT.csv")

			Stream.Foreach(*) { stream_idx =>

				Pipe {
					val packet = inbus.value
					packet_use1.enq(packet)
					packet_use2.enq(packet)
				}

				Pipe {
					val packet = packet_use1.deq()
					val eth = 112
					val ip = 160
					val shift_amounts = Seq.tabulate(num_fields){i => (eth + ip + (i * 32)).to[I16]}
					Foreach(0 until num_fields par num_fields){ i =>
						val mux1H_conds = Seq.tabulate(num_fields){j => j.to[I32] === i}
						val shifted_pkt = oneHotMux(mux1H_conds, shift_amounts.map{amt => packet.tdata.as[U512] >> amt})
						input(i) = cat(shifted_pkt.bits(7::0), shifted_pkt.bits(15::8), shifted_pkt.bits(23::16), shifted_pkt.bits(31::24)).as[T]
					}
					dummy_stageinput_fifo.enq(input(num_fields - 1))
				}

				Pipe {

					val dummy = dummy_stageinput_fifo.deq()

					List.tabulate(L0_Dim0) { i =>
						val partial_results = List.tabulate(L0_Dim1) { j =>
							L0_W_LUT(i, j) * input(j)
						}
						val w = partial_results.reduceTree {_+_}
						L0_res(i) = max(w + L0_B_LUT(i), 0)
					}

					dummy_stage0_fifo.enq(L0_res(L0_Dim0 - 1))

				}

				Pipe {

					val dummy = dummy_stage0_fifo.deq()

					List.tabulate(L1_Dim0) { i =>
						val partial_results = List.tabulate(L1_Dim1) { j =>
							L1_W_LUT(i, j) * L0_res(j)
						}
						val w = partial_results.reduceTree {_+_}
						L1_res(i) = max(w + L1_B_LUT(i), 0)
					}

					dummy_stage1_fifo.enq(L1_res(L1_Dim0 - 1))

				}

				Pipe {

					val dummy = dummy_stage1_fifo.deq()

					List.tabulate(L2_Dim0) { i =>
						val partial_results = List.tabulate(L2_Dim1) { j =>
							L2_W_LUT(i, j) * L1_res(j)
						}
						val w = partial_results.reduceTree {_+_}
						L2_res(i) = max(w + L2_B_LUT(i), 0)
					}

					dummy_stage2_fifo.enq(L2_res(L2_Dim0 - 1))

				}

				Pipe {

					val dummy = dummy_stage2_fifo.deq()

					List.tabulate(L3_Dim0) { i =>
						val partial_results = List.tabulate(L3_Dim1) { j =>
							L3_W_LUT(i, j) * L2_res(j)
						}
						val w = partial_results.reduceTree {_+_}
						L3_res(i) = max(w + L3_B_LUT(i), 0)
					}

					dummy_stage3_fifo.enq(L3_res(L3_Dim0 - 1))

				}

				Pipe {

					val dummy = dummy_stage3_fifo.deq()

					List.tabulate(L4_Dim0) { i =>
						val partial_results = List.tabulate(L4_Dim1) { j =>
							L4_W_LUT(i, j) * L3_res(j)
						}
						val w = partial_results.reduceTree {_+_}
						L4_res(i) = max(w + L4_B_LUT(i), 0)
					}

					dummy_stage4_fifo.enq(L4_res(L4_Dim0 - 1))

				}

				Pipe {

					val dummy = dummy_stage4_fifo.deq()

					List.tabulate(L5_Dim0) { i =>
						val partial_results = List.tabulate(L5_Dim1) { j =>
							L5_W_LUT(i, j) * L4_res(j)
						}
						val w = partial_results.reduceTree {_+_}
						L5_res(i) = max(w + L5_B_LUT(i), 0)
					}

					dummy_stage5_fifo.enq(L5_res(L5_Dim0 - 1))

				}

				Pipe {

					val dummy = dummy_stage5_fifo.deq()

					List.tabulate(L6_Dim0) { i =>
						val partial_results = List.tabulate(L6_Dim1) { j =>
							L6_W_LUT(i, j) * L5_res(j)
						}
						val w = partial_results.reduceTree {_+_}
						L6_res(i) = max(w + L6_B_LUT(i), 0)
					}

					dummy_stage6_fifo.enq(L6_res(L6_Dim0 - 1))

				}

				Pipe {

					val dummy = dummy_stage6_fifo.deq()

					List.tabulate(L7_Dim0) { i =>
						val partial_results = List.tabulate(L7_Dim1) { j =>
							L7_W_LUT(i, j) * L6_res(j)
						}
						val w = partial_results.reduceTree {_+_}
						L7_res(i) = max(w + L7_B_LUT(i), 0)
					}

					dummy_stage7_fifo.enq(L7_res(L7_Dim0 - 1))

				}

				Pipe {

					val dummy = dummy_stage7_fifo.deq()

					List.tabulate(L8_Dim0) { i =>
						val partial_results = List.tabulate(L8_Dim1) { j =>
							L8_W_LUT(i, j) * L7_res(j)
						}
						val w = partial_results.reduceTree {_+_}
						L8_res(i) = max(w + L8_B_LUT(i), 0)
					}

					dummy_stage8_fifo.enq(L8_res(L8_Dim0 - 1))

				}

				Pipe {

					val dummy = dummy_stage8_fifo.deq()

					List.tabulate(L9_Dim0) { i =>
						val partial_results = List.tabulate(L9_Dim1) { j =>
							L9_W_LUT(i, j) * L8_res(j)
						}
						val w = partial_results.reduceTree {_+_}
						L9_res(i) = max(w + L9_B_LUT(i), 0)
					}

					dummy_stage9_fifo.enq(L9_res(L9_Dim0 - 1))

				}

				Pipe {

					val dummy = dummy_stage9_fifo.deq()

					List.tabulate(L10_Dim0) { i =>
						val partial_results = List.tabulate(L10_Dim1) { j =>
							L10_W_LUT(i, j) * L9_res(j)
						}
						val w = partial_results.reduceTree {_+_}
						L10_res(i) = w + L10_B_LUT(i)
					}

					dummy_stage10_fifo.enq(L10_res(L10_Dim0 - 1))

				}

				Pipe {

					val dummy = dummy_stage10_fifo.deq()

					val maxVal = Reduce(Reg[T])(2 par 2){ i =>
						L10_res(i)
					}{(a,b) => max(a,b)}

					val decision = Reduce(Reg[I32])(2 par 2){ i =>
						mux(L10_res(i) == maxVal.value, i, -1)
					}{(a,b) => max(a,b)}

					dummy_stage11_fifo.enq(decision)

				}

				Pipe {
					val decision = dummy_stage11_fifo.deq()
					val packet = packet_use2.deq()
					val newPacket = AxiStream512((packet.tdata.as[U512]) | (decision.as[U512] << 504), packet.tstrb, packet.tkeep, packet.tlast, packet.tid, 1, 0)
					outbus := newPacket
				}

			}

		}
		assert(1 == 1)

	}

}

